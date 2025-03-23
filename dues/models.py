from django.db import models, transaction
from django.conf import settings
from borrowing.models import Borrow
from django.core.mail import send_mail
from django.utils import timezone
import razorpay
from django.utils.timezone import now, timedelta



class Due(models.Model):
    borrow = models.OneToOneField(Borrow, on_delete=models.CASCADE, related_name="due")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    
    @property
    def student(self):
        """Get student from the associated borrow record"""
        return self.borrow.student
        
    def calculate_fine_amount(self):
        """Calculate fine amount without modifying the database."""
        daily_fine = 20.00
        
        if self.borrow.is_overdue:
            if self.borrow.return_date:
                # Book returned late
                overdue_days = (self.borrow.return_date - self.borrow.due_date).days
            else:
                # Book not returned and is overdue
                overdue_days = (timezone.now() - self.borrow.due_date).days
            return max(0, overdue_days * daily_fine)
        
        return 0.00

    def update_fine(self):
        """Update the fine amount in the database."""
        fine_amount = self.calculate_fine_amount()
        if fine_amount != self.amount:
            self.amount = fine_amount
            self.save(update_fields=['amount', 'updated_at'])
        return self.amount
    
    def send_reminder_email(self):
        """Send a reminder email to the student for unpaid dues."""
        try:
            if not self.is_paid and self.amount > 0:
                # Update fine before sending reminder
                self.update_fine()
                
                subject = "Reminder: NITK Library Dues Pending"
                message = (f"Dear {self.student.user.username},\n\n"
                           f"This is a reminder that you have an outstanding due of INR {self.amount}.\n"
                           f"Please clear your dues at the earliest to avoid further fines.\n\n"
                           "NITK Library")
                send_mail(
                    subject,
                    message,
                    "library@nitk.edu.in",
                    [self.student.user.email]
                )
                return True
        except Exception as e:
            return False
        return False
    
    def __str__(self):
        status = "Paid" if self.is_paid else "Unpaid"
        return f"{status} Due of ₹{self.amount} for {self.borrow}"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('created', 'Order Created'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    due = models.ForeignKey(Due, on_delete=models.CASCADE, related_name="payments")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    is_successful = models.BooleanField(default=False)
    failure_reason = models.TextField(blank=True, null=True)
    
    def create_razorpay_order(self):
        """Create a Razorpay order and return the order details."""
        try:
            # Ensure API keys are configured
            if not hasattr(settings, 'RAZORPAY_KEY') or not hasattr(settings, 'RAZORPAY_SECRET'):
                raise ValueError("Payment gateway configuration missing")
            
            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY,
                settings.RAZORPAY_SECRET
            ))
            
            # Ensure due amount is up to date
            self.due.update_fine()
            
            # Validate due amount
            if self.due.amount <= 0:
                raise ValueError("Cannot create payment for due with zero or negative amount")
                
            if self.due.is_paid:
                raise ValueError("This due is already paid")
            
            # Create order with idempotency
            order_data = client.order.create({
                "amount": int(self.due.amount * 100),  # Convert to paisa
                "currency": "INR",
                "payment_capture": "1",
                "notes": {
                    "due_id": str(self.due.id),
                    "student_id": str(self.due.student.id),
                    "book_title": self.due.borrow.book.title
                }
            })
            
            # Update payment record
            self.razorpay_order_id = order_data["id"]
            self.amount_paid = self.due.amount
            self.status = 'created'
            self.save()
            
            return order_data
            
        except razorpay.errors.BadRequestError as e:
            self.status = 'failed'
            self.failure_reason = f"Bad request to payment gateway: {str(e)}"
            self.save()
            raise
        except Exception as e:
            self.status = 'failed'
            self.failure_reason = f"Error creating payment: {str(e)}"
            self.save()
            raise

    @transaction.atomic
    def complete_payment(self, razorpay_payment_id, razorpay_signature):
        """Verify and mark payment as complete after successful payment."""
        # Check if already processed
        if self.is_successful:
            return True
            
        try:
            # Verify payment signature
            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY,
                settings.RAZORPAY_SECRET
            ))
            
            params_dict = {
                'razorpay_order_id': self.razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            # This will raise an exception if verification fails
            client.utility.verify_payment_signature(params_dict)
            
            # Update payment record with transaction data
            self.razorpay_payment_id = razorpay_payment_id
            self.razorpay_signature = razorpay_signature
            self.is_successful = True
            self.status = 'successful'
            self.save()
            
            # Mark due as paid - wrapped in the same transaction
            self.due.is_paid = True
            self.due.save(update_fields=['is_paid', 'updated_at'])
            
            # Send receipt email
            self.send_receipt_email()
            
            return True
            
        except razorpay.errors.SignatureVerificationError:
            self.status = 'failed'
            self.failure_reason = "Payment signature verification failed"
            self.save()
            return False
            
        except Exception as e:
            self.status = 'failed'
            self.failure_reason = f"Error processing payment: {str(e)}"
            self.save()
            return False
        
    def verify_payment_status(self):
        """Verify payment status directly with Razorpay."""
        if self.is_successful:
            return True
            
        try:
            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY,
                settings.RAZORPAY_SECRET
            ))
            
            # Fetch order data from Razorpay
            order_data = client.order.fetch(self.razorpay_order_id)
            
            # Check if the order is paid
            if order_data.get('status') == 'paid':
                # Get associated payments
                payments = client.order.payments(self.razorpay_order_id)
                
                if payments and len(payments.get('items', [])) > 0:
                    payment = payments['items'][0]
                    
                    # Mark as successful if not already
                    if not self.is_successful:
                        self.razorpay_payment_id = payment['id']
                        self.is_successful = True
                        self.status = 'successful'
                        self.save()
                        
                        # Mark due as paid
                        self.due.is_paid = True
                        self.due.save()
                        
                        # Send receipt
                        self.send_receipt_email()
                        
                    return True
            
            return False
            
        except Exception as e:
            return False
        
    def send_receipt_email(self):
        try:
            """Send a payment receipt to the student."""
            subject = "NITK Library Dues Payment Receipt"
            message = (f"Dear {self.due.student.user.username},\n\n" 
                        f"Your payment of INR {self.amount_paid} has been received.\n" 
                        f"Order ID: {self.razorpay_order_id}\n"
                        f"Payment ID: {self.razorpay_payment_id}\n"
                        f"Payment Date: {self.payment_date.strftime('%d %b %Y, %I:%M %p')}\n\n"
                        "Thank you for clearing your dues.\n\n"
                        "NITK Library")
                                   
            send_mail(
                    subject, 
                    message, 
                    'library@nitk.edu.in', 
                    [self.due.student.user.email]
            )
        except Exception as e:
            pass
            
    
    @property
    def is_expired(self):
        """Check if payment order has expired (older than 24 hours)."""
        expiration_time = timedelta(hours=24)
        return now() > (self.payment_date + expiration_time)
    
    def __str__(self):
        status_text = "Successful" if self.is_successful else self.get_status_display()
        return f"Payment of ₹{self.amount_paid} for {self.due} ({status_text})"


def send_due_reminders():
    """Send reminder emails for all unpaid dues every 3 days."""
    # Find dues that haven't been updated in 3+ days and are unpaid
    unpaid_dues = Due.objects.filter(
            is_paid=False, 
            updated_at__lte=now() - timedelta(days=3),
            amount__gt=0
        )
        
    for due in unpaid_dues:
        due.send_reminder_email()



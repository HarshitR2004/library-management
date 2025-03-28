from django.db import models, transaction
from borrowing.models import Borrow
from django.utils import timezone
from borrowing.utils import send_notification_email



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
                overdue_days = (self.borrow.return_date - self.borrow.due_date).days
            else:
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
    
    
    def __str__(self):
        status = "Paid" if self.is_paid else "Unpaid"
        return f"{status} Due of ₹{self.amount} for {self.borrow}"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ]
    
    due = models.ForeignKey(Due, on_delete=models.CASCADE, related_name="payments")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
 
    
    payment_reference = models.CharField(max_length=100, unique=True, help_text="Manual payment reference number", default="123")
    processed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, null=True)
    is_successful = models.BooleanField(default=False)
    failure_reason = models.TextField(blank=True, null=True)
    
    
    def send_receipt_email(self):
        """Send a payment receipt to the student."""
        message = f"""Dear {self.due.student.user.username}
        
    Your payment of INR {self.amount_paid} has been received and processed.
    Payment Reference: {self.payment_reference}
    Payment Date: {self.payment_date.strftime('%d %b %Y, %I:%M %p')}
    
    Thank you for clearing your dues.
    
    Best Regards,
    NITK Library"""
        
        return send_notification_email(
            subject=f"NITK Library - Payment Receipt for Due {self.due.id}",
            recipient=self.due.student.user.email,
            message=message
        )

   
    @transaction.atomic
    def record_manual_payment(self, librarian):
        """Record a manual payment made at the library."""
        if self.due.is_paid:
            raise ValueError("This due is already paid")

        self.status = 'successful'
        self.processed_by = librarian
        self.payment_reference = f"MANUAL-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        self.is_successful = True
        self.save()
        
        self.due.is_paid = True
        self.due.save(update_fields=['is_paid', 'updated_at'])
        self.send_receipt_email()
        
        return True



    def __str__(self):
        status_text = "Successful" if self.is_successful else self.get_status_display()
        return f"Payment of ₹{self.amount_paid} for {self.due} ({status_text})"





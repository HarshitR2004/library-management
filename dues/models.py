from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from borrowing.models import Borrow
from django.core.mail import send_mail
import uuid

class Due(models.Model):
    borrow = models.OneToOneField(Borrow, on_delete=models.CASCADE, related_name="due")
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def calculate_due(self, daily_fine=10):
        """Calculate the fine based on the number of overdue days."""
        if self.borrow.is_returned and self.borrow.return_date > self.borrow.due_date:
            overdue_days = (self.borrow.return_date - self.borrow.due_date).days
            self.amount = overdue_days * daily_fine
            self.save()

class Payment(models.Model):
    due = models.ForeignKey(Due, on_delete=models.CASCADE, related_name="payments")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Payment of {self.amount_paid} for Due {self.due.id}"
    
    def send_recipt_mail(self):
        """Send a payment receipt to the student."""
        subject = "NITK Library Dues Payment Receipt"
        message = (f"Dear {self.due.student.username},\n\n" 
                   f"Your payment of INR {self.amount_paid} has been received.\n" 
                   f"Transaction ID: {self.transaction_id}\n" 
                   "Thank you for clearing your dues.\n\n NITK Library")
        send_mail(subject, message, "library@domain.com", [self.due.student.email])
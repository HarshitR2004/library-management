from django.db import models
from django.core.mail import send_mail
from django.utils import timezone
from django.core.exceptions import ValidationError
from books.models import Book
from users.models import Student  
from books.models import Journal, Book
from borrowing.utils import send_notification_email
from django.conf import settings

class Borrow(models.Model):
    """Model to track book borrow transactions with librarian approval."""

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Returned', 'Returned'),
        ('Pending Return','Pending Return')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, null=True, blank=True)
    borrow_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    is_overdue = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def clean(self):
        """Validate the borrow object."""
        if (self.book is None and self.journal is None) or (self.book is not None and self.journal is not None):
            raise ValidationError("Either a book or journal must be specified, but not both.")
            
        if self.journal and not self.journal.is_approved:
            raise ValidationError("Journal must be approved by a librarian before it can be borrowed.")

    def save(self, *args, **kwargs):
        """Ensure book availability and update inventory only after approval."""
        self.clean()
        if self.book and self.book.available_copies <= 0:
            raise ValueError(f"No available copies of {self.book.title}.")
            
        if self.student.borrow_limit <= 0:
            raise ValueError("Borrow limit reached")
        
        super().save(*args, **kwargs)

    @property
    def item(self):
        """Return the borrowed item (book or journal)."""
        return self.book if self.book else self.journal
        
    @property
    def item_type(self):
        """Return the type of borrowed item."""
        return "book" if self.book else "journal"

    def send_approval_email(self):
        """Send simple approval email"""
        message = f"""Dear {self.student.user.get_full_name() or self.student.user.username},

Your request to borrow "{self.book.title if self.book else self.journal.title}" has been approved.

Due Date: {self.due_date.strftime('%Y-%m-%d')}
Item Type: {self.item_type.title()}

Please return the item before the due date to avoid fines.

Best regards,
NITK Library"""

        return send_notification_email(
            subject=f"NITK Library - {self.item_type.title()} Borrow Request Approved",
            recipient=self.student.user.email,
            message=message
        )

    def send_rejection_email(self):
        """Send simple rejection email"""
        message = f"""Dear {self.student.user.get_full_name() or self.student.user.username},

Your request to borrow "{self.book.title if self.book else self.journal.title}" has been rejected.

Please contact the library if you need more information.

Best regards,
NITK Library"""

        return send_notification_email(
            subject=f"NITK Library - {self.item_type.title()} Borrow Request Rejected",
            recipient=self.student.user.email,
            message=message
        )

    def send_return_confirmation_email(self):
        """Send simple return confirmation email"""
        message = f"""Dear {self.student.user.get_full_name() or self.student.user.username},

Your return of "{self.book.title if self.book else self.journal.title}" has been processed.

Return Date: {self.return_date.strftime('%Y-%m-%d')}
Status: {"Overdue" if self.is_overdue else "On time"}

Thank you for using NITK Library services.

Best regards,
NITK Library"""

        return send_notification_email(
            subject=f"NITK Library - {self.item_type.title()} Return Confirmation",
            recipient=self.student.user.email,
            message=message
        )

    def approve(self):
        """Librarian approves the request"""
        if self.status != 'Pending':
            raise ValueError("Request is already processed.")

        self.status = 'Approved'
        self.due_date = timezone.now() + timezone.timedelta(days=14)

        if self.book:
            self.book.available_copies -= 1
            self.book.save()
        elif self.journal:
            self.journal.available_copies -= 1
            self.journal.save()
            
        self.student.borrow_limit -= 1
        self.student.save()
        self.save()
        
        # Send approval email
        self.send_approval_email()

    def reject(self):
        """Librarian rejects the request"""
        if self.status != 'Pending':
            raise ValueError("Request is already processed.")

        self.status = 'Rejected'
        self.save()
        
        # Send rejection email
        self.send_rejection_email()

    def return_book(self):
        """Process item return"""
        if self.is_returned:
            raise ValueError("This item has already been returned.")
        
        self.return_date = timezone.now()
        self.is_returned = True
        self.status = "Returned"
        self.is_overdue = self.return_date > self.due_date

        if self.book:
            self.book.available_copies += 1
            self.book.save()
        elif self.journal:
            self.journal.available_copies += 1
            self.journal.save()
            
        self.student.borrow_limit += 1
        self.student.save()
        self.save()
        
        # Send return confirmation email
        self.send_return_confirmation_email()

    def __str__(self):
        return f"{self.student.user.username} - {self.item.title} ({self.status})"


from django.db import models
from django.core.mail import send_mail
from django.utils import timezone
from django.core.exceptions import ValidationError
from books.models import Book
from users.models import Student  
from books.models import Journal, Book

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

    def approve(self):
        """Librarian approves the request, updates inventory and due date."""
        if self.status != 'Pending':
            raise ValueError("Request is already processed.")

        self.status = 'Approved'
        self.due_date = timezone.now() + timezone.timedelta(days=14)

        if self.book:
            self.book.available_copies -= 1
            self.book.save()
        self.student.borrow_limit -= 1
        self.student.save()

        self.save()
        
        try:
            send_mail(
                "Book Borrow Request Approved", 
                f"Dear {self.student.user.username},\n\n"
                f"Your request to borrow '{self.item.title}' has been approved.\n"
                f"Due date: {self.due_date.strftime('%Y-%m-%d')}\n\n"
                f"Best regards,\n NITK Library", 
                "harshithranjan6971+test_lib1@gmail.com", 
                [self.student.user.email],
                fail_silently=True 
            )
        except Exception as e:
            print(f"Failed to send approval email: {e}")

    def reject(self):
        """Librarian rejects the request."""
        if self.status != 'Pending':
            raise ValueError("Request is already processed.")

        self.status = 'Rejected'
        self.save()
        
        send_mail(
        "Book Borrow Request Rejected", 
        f"Dear {self.student.user.username},\n\n"
        f"Unfortunately, your request to borrow '{self.item.title}' has been rejected.\n"
        f"Please contact the library for more information.\n\n"
        f"Best regards,\n NITK Library", 
        "harshithranjan6971+test_lib1@gmail.com", 
        [self.student.user.email]
    )

    def return_book(self):
        """Mark book as returned, update inventory, and check for overdue status."""
        if self.is_returned:
            raise ValueError("This book has already been returned.")
        
        self.return_date = timezone.now()
        self.is_returned = True
        self.status = "Returned"

        if self.return_date > self.due_date:
            self.is_overdue = True

        if self.book:
            self.book.available_copies += 1
            self.book.save()
        self.student.borrow_limit += 1
        self.student.save()

        self.save()
        
        try:
            send_mail("Book Return Confirmation", 
                f"Dear {self.student.user.username},\n\nYou have returned '{self.item.title}'.", 
                "harshithranjan6971+test_lib1@gmail.com", 
                [self.student.user.email],
                fail_silently=True
            )
        except Exception as e:
            print(f"Failed to send return confirmation email: {e}")

    def __str__(self):
        return f"{self.student.user.username} - {self.item.title} ({self.status})"


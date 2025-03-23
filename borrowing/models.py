from django.db import models
from django.core.mail import send_mail
from django.utils import timezone
from books.models import Book
from users.models import Student  
# from dues.models import Due

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
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    is_overdue = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def save(self, *args, **kwargs):
        """Ensure book availability and update inventory only after approval."""
        if self.book.available_copies <= 0:
            raise ValueError(f"No available copies of {self.book.title}.")
            
        if self.student.borrow_limit <= 0:
            raise ValueError("Borrow limit reached")
        
        super().save(*args, **kwargs)

    def approve(self):
        """Librarian approves the request, updates inventory and due date."""
        if self.status != 'Pending':
            raise ValueError("Request is already processed.")

        self.status = 'Approved'
        self.due_date = timezone.now() + timezone.timedelta(days=14)

        self.book.available_copies -= 1
        self.book.save()
        
        self.student.borrow_limit -= 1
        self.student.save()

        self.save()
        
        send_mail(
        "Book Borrow Request Approved", 
        f"Dear {self.student.user.username},\n\n"
        f"Your request to borrow '{self.book.title}' has been approved.\n"
        f"Due date: {self.due_date.strftime('%Y-%m-%d')}\n\n"
        f"Best regards,\n NITK Library", 
        "library@domain.com", 
        [self.student.user.email]
    )

    def reject(self):
        """Librarian rejects the request."""
        if self.status != 'Pending':
            raise ValueError("Request is already processed.")

        self.status = 'Rejected'
        self.save()
        
        send_mail(
        "Book Borrow Request Rejected", 
        f"Dear {self.student.user.username},\n\n"
        f"Unfortunately, your request to borrow '{self.book.title}' has been rejected.\n"
        f"Please contact the library for more information.\n\n"
        f"Best regards,\n NITK Library", 
        "library@domain.com", 
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
            # due = Due.objects.get_or_create(borrow=self)
            # due.calculate_due()  

        self.book.available_copies += 1
        self.book.save()
        self.student.borrow_limit += 1
        self.student.save()

        self.save()
        send_mail("Book Return Confirmation", 
              f"Dear {self.student.username},\n\nYou have returned '{self.book.title}'.", 
              "library@domain.com", [self.student.email])

    def __str__(self):
        return f"{self.student.user.username} - {self.book.title} ({self.status})"


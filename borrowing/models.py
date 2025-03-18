from django.db import models
from django.utils import timezone
from books.models import Book
from users.models import Student  

class Borrow(models.Model):
    """Model to track book borrow transactions."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    is_overdue = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """Ensure only students can borrow, check inventory, and reduce book count."""
        if not self.pk:  
            if self.book.available_copies <= 0:
                raise ValueError(f"No available copies of {self.book.title}.")
            
            self.due_date = self.borrow_date + timezone.timedelta(days=14)
            
            self.book.available_copies -= 1
            self.book.save()

        super().save(*args, **kwargs)

        self.student.borrow_limit -= 1
        self.student.save()

    def return_book(self):
        """Mark the book as returned, update inventory, and restore borrow limit."""
        if self.is_returned:
            raise ValueError("This book has already been returned.")

        self.return_date = timezone.now()
        self.is_returned = True

        if self.return_date > self.due_date:
            self.is_overdue = True  

        self.book.available_copies += 1
        self.book.save()
        self.student.borrow_limit += 1
        self.student.save()

        self.save()

    def __str__(self):
        return f"{self.student.user.username} borrowed {self.book.title} (Due: {self.due_date.strftime('%Y-%m-%d')})"

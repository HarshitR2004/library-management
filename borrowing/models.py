from django.db import models
from django.core.validators import MinValueValidator
from django.utils.timezone import now
from users.models import User  
from books.models import Book, Journal 

class Borrowing(models.Model):
    """Tracks book and journal borrowing by users."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)
    journal = models.ForeignKey(Journal, on_delete=models.SET_NULL, null=True, blank=True)
    borrowed_at = models.DateTimeField(default=now)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    faculty_approved = models.BooleanField(default=False) 

    def save(self, *args, **kwargs):
        """Prevents borrowing if no copies are available."""
        if self.book and self.book.available_copies <= 0:
            raise ValueError(f"No copies available for '{self.book.title}'")
        if self.journal and self.journal.available_copies <= 0:
            raise ValueError(f"No copies available for '{self.journal.title}'")
        if self.journal and not self.faculty_approved:
            raise ValueError("Faculty approval required for journals/magazines.")
        if not self.user.library_card_number:
            raise ValueError(f"Library Card not avalliable for {self.user.name}")
        
        # Reduce available copies when borrowing
        if not self.returned_at:
            if self.book:
                self.book.available_copies -= 1
                self.book.save()
            if self.journal:
                self.journal.available_copies -= 1
                self.journal.save()

        super().save(*args, **kwargs)

    def return_item(self):
        """Handles returning a book or journal."""
        self.returned_at = now()
        
        # Restore available copies
        if self.book:
            self.book.available_copies += 1
            self.book.save()
        if self.journal:
            self.journal.available_copies += 1
            self.journal.save()
        
        self.save()

    def __str__(self):
        item = self.book.title if self.book else self.journal.title
        return f"{self.user.username} borrowed {item} on {self.borrowed_at}"

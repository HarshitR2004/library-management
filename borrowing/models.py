from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now, timedelta
from books.models import Journal

class BorrowingStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RETURNED = "returned"

    CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (RETURNED, "Returned"),
    ]

class Borrowing(models.Model):
    """Tracks book and journal borrowing by users."""
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    book = models.ForeignKey('books.Book', on_delete=models.SET_NULL, null=True, blank=True)
    journal = models.ForeignKey(Journal, on_delete=models.SET_NULL, null=True, blank=True)
    borrowed_at = models.DateTimeField(default=now)
    due_date = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    admin_approved = models.BooleanField(default=False)
    librarian_approved = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=BorrowingStatus.CHOICES, default=BorrowingStatus.PENDING)

    def check_conditions(self):
        """Check borrowing conditions and set rejection status if necessary."""
        if self.book and self.journal:
            self.status = BorrowingStatus.REJECTED
            return "Cannot borrow both a book and a journal in the same transaction."
        
        if self.book:
            if self.book.available_copies <= 0:
                self.status = BorrowingStatus.REJECTED
                return f"No copies available for '{self.book.title}'."
            if not self.librarian_approved:
                self.status = BorrowingStatus.REJECTED
                return "Librarian approval required for borrowing books."
        
        if self.journal:
            if self.journal.available_copies <= 0:
                self.status = BorrowingStatus.REJECTED
                return f"No copies available for '{self.journal.title}'."
            if not self.admin_approved:
                self.status = BorrowingStatus.REJECTED
                return "Admin approval required for journals/magazines."

        if self.user.is_student() and not self.user.student.library_card_number:
            self.status = BorrowingStatus.REJECTED
            return f"Library Card not available for {self.user.username}."

        # Prevent duplicate borrowing of the same book/journal
        if self.book and Borrowing.objects.filter(user=self.user, book=self.book, status=BorrowingStatus.APPROVED, returned_at__isnull=True).exists():
            self.status = BorrowingStatus.REJECTED
            return f"{self.user.username} already borrowed '{self.book.title}' and has not returned it."
        
        return None  # No issues found

    def save(self, *args, **kwargs):
        """Validate borrowing conditions and update status before saving."""
        rejection_reason = self.check_conditions()
        if rejection_reason:
            print(f"Borrowing request rejected: {rejection_reason}")

        # If approved, reduce available copies
        if self.status == BorrowingStatus.APPROVED:
            if self.book:
                self.book.available_copies -= 1
                self.book.save()
            if self.journal:
                self.journal.available_copies -= 1
                self.journal.save()

        # Set default due date (2 weeks from borrowing date)
        if not self.due_date:
            self.due_date = now() + timedelta(weeks=2)

        super().save(*args, **kwargs)

    def approve(self):
        """Approve borrowing request if conditions are met."""
        if self.status == BorrowingStatus.PENDING:
            if self.book:
                self.librarian_approved = True
            if self.journal:
                self.admin_approved = True
            self.status = BorrowingStatus.APPROVED
            self.save()

    def reject(self, reason=""):
        """Reject borrowing request."""
        self.status = BorrowingStatus.REJECTED
        self.save()
        print(f"Borrowing request rejected: {reason}")

    def return_book(self):
        """Mark book/journal as returned and restore available copies."""
        if self.status == BorrowingStatus.APPROVED:
            self.returned_at = now()
            self.status = BorrowingStatus.RETURNED

            if self.book:
                self.book.available_copies += 1
                self.book.save()
            if self.journal:
                self.journal.available_copies += 1
                self.journal.save()

            self.save()

    def __str__(self):
        item = self.book.title if self.book else self.journal.title
        return f"{self.user.username} borrowed {item} ({self.status})"

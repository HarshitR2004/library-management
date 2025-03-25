from django.db import models
from books.models import Book, Journal
from users.models import User


class ReadingList(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['book', 'user']
    
    
    def __str__(self):
        return f"Reading List of {self.user}"
    
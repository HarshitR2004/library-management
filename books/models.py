from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from enum import Enum

class Author(models.Model):
    """Stores author details."""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Book(models.Model):
    """Represents books in the library."""
    
    GenreChoices = [
    ('Metallurgy', 'METALLURGY'),
    ('Computer Science', 'CS'),
    ('ECE', 'ECE'),
    ('EEE', 'EEE'),
    ('Mechanical', 'MECHANICAL'),
    ('Civil', 'CIVIL'),
    ('AI', 'AI'),
    ('Data Science', 'DATA_SCIENCE'),
    ('Mining', 'MINING'),
    ('IT', 'IT')
]

    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    publisher = models.CharField(max_length=255)
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=8, decimal_places=2)
    genre = models.CharField(max_length=50, choices=GenreChoices)
    topics = models.TextField(blank=True, null=True)
    available_copies = models.IntegerField(default=1, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.title

class Journal(models.Model):
    """Represents academic journals, magazines, and newspapers."""
    
    JOURNAL_TYPE_CHOICES = [
        ("Journal", "Journal"),
        ("Magazine", "Magazine"),
        ("Newspaper", "Newspaper"),
    ]

    title = models.CharField(max_length=255, db_index=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    publisher = models.CharField(max_length=255)
    journal_type = models.CharField(max_length=50, choices=JOURNAL_TYPE_CHOICES)
    publication_date = models.DateField()
    available_copies = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    is_approved = models.BooleanField(default=False)
    
    issn = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
        help_text="Enter ISSN only for Journals"
    )

    def clean(self):
        """Ensure ISSN is required only for Journals."""
        if self.journal_type == "Journal" and not self.issn:
            raise ValidationError("ISSN is required for Journals.")
        elif self.journal_type != "Journal" and self.issn:
            raise ValidationError("ISSN should only be provided for Journals.")

    def save(self, *args, **kwargs):
        """Override save to run clean() before saving."""
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        journal_info = f"{self.title} ({self.journal_type}) - {self.publication_date} by {self.author.name}"
        if self.journal_type == "Journal" and self.issn:
            journal_info += f" [ISSN: {self.issn}]"
        return journal_info



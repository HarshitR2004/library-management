from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from enum import Enum

class Author(models.Model):
    """Stores author details."""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class GenreChoices(Enum):
    METALLURGY = "Metallurgy"
    CS = "Computer Science"
    ECE = "ECE"
    EEE = "EEE"
    MECHANICAL = "Mechanical"
    CIVIL = "Civil"
    AI = "AI"
    DATA_SCIENCE = "Data Science"
    MINING = "Mining"
    IT = "IT"

    @classmethod
    def choices(cls):
        return [(tag.value, tag.name.replace("_", " ")) for tag in cls]

class Book(models.Model):
    """Represents books in the library."""
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    publisher = models.CharField(max_length=255)
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=8, decimal_places=2)
    genre = models.CharField(max_length=50, choices=GenreChoices.choices())
    topics = models.TextField(blank=True, null=True)
    available_copies = models.IntegerField(default=1, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.title} by {self.author.name}"

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

    def __str__(self):
        return f"{self.title} ({self.journal_type}) - {self.publication_date} by {self.author.name}"



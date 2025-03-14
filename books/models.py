from django.db import models
from django.core.validators import MinValueValidator 

class Author(models.Model):
    """Stores author details."""
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    """Represents books in the engineering college library."""
    
    GENRE_CHOICES = [
        ("Metallurgy", "Metallurgy"),
        ("Computer Science", "Computer Science"),
        ("ECE", "ECE"),
        ("EEE", "EEE"),  
        ("Mechanical", "Mechanical"),
        ("Civil", "Civil"),
        ("AI", "AI"),
        ("Data Science", "Data Science"),
        ("Mining", "Mining"),
        ("IT", "IT"),
    ]

    title = models.CharField(max_length=255)
    author = models.ManyToManyField(Author)  
    publisher = models.CharField(max_length=255)
    pages = models.IntegerField(validators=[MinValueValidator(1)])  # Ensures at least 1 page
    price = models.DecimalField(max_digits=8)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)  # Restricts genre selection
    topics = models.TextField(blank=True, null=True)  # Stores book topics

    def __str__(self):
        authors = ", ".join(author.name for author in self.author.all())
        return f"{self.title} by {authors}"

# Journals class to store journals, magazines, newspapers
class Journal(models.Model):
    """Represents academic journals, magazines, and newspapers in the e-library."""

    JOURNAL_TYPE_CHOICES = [
        ("Journal", "Journal"),
        ("Magazine", "Magazine"),
        ("Newspaper", "Newspaper"),
    ]

    title = models.CharField(max_length=255, db_index=True) #Title of the journal/ can also be used for newspaper and magzine titles (TOI, Nature etc)
    authors = models.ManyToManyField("Author", blank=True, related_name="journals")  
    publisher = models.CharField(max_length=255)
    journal_type = models.CharField(max_length=50, choices=JOURNAL_TYPE_CHOICES)
    publication_date = models.DateField()

    # Only for journals (ISSN is unique but some may not have it)
    issn = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
        help_text="Enter ISSN only for Journals"
    )

    def __str__(self):
        return f"{self.title} ({self.journal_type}) - {self.publication_date}"


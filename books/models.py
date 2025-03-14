from django.db import models
from django.core.validators import MinValueValidator 

class Author(models.Model):
    """Stores author details."""
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    """Represents books in the library."""
    
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
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=8, decimal_places=2)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    topics = models.TextField(blank=True, null=True)
    available_copies = models.IntegerField(default=1)

    @classmethod
    def create_book(cls, title, authors, publisher, pages, price, genre, topics="", available_copies=1):
        """Creates a new book entry in the database."""
        book = cls.objects.create(
            title=title,
            publisher=publisher,
            pages=pages,
            price=price,
            genre=genre,
            topics=topics,
            available_copies=available_copies
        )
        book.author.set(authors)
        book.save()
        return book

    def __str__(self):
        authors = ", ".join(author.name for author in self.author.all())
        return f"{self.title} by {authors}"

class Journal(models.Model):
    """Represents academic journals, magazines, and newspapers."""

    JOURNAL_TYPE_CHOICES = [
        ("Journal", "Journal"),
        ("Magazine", "Magazine"),
        ("Newspaper", "Newspaper"),
    ]

    title = models.CharField(max_length=255, db_index=True)
    authors = models.ManyToManyField("Author", blank=True, related_name="journals")  
    publisher = models.CharField(max_length=255)
    journal_type = models.CharField(max_length=50, choices=JOURNAL_TYPE_CHOICES)
    publication_date = models.DateField()
    available_copies = models.IntegerField(default=1)
    issn = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
        help_text="Enter ISSN only for Journals"
    )

    @classmethod
    def create_journal(cls, title, authors, publisher, journal_type, publication_date, available_copies, issn=None):
        """Creates a new journal entry in the database."""
        journal = cls.objects.create(
            title=title,
            publisher=publisher,
            journal_type=journal_type,
            publication_date=publication_date,
            available_copies=available_copies,
            issn=issn
        )
        journal.authors.set(authors)
        journal.save()
        return journal

    def __str__(self):
        return f"{self.title} ({self.journal_type}) - {self.publication_date}"


from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from books.models import Book, Journal


class UserRoles:
    STUDENT = "student"
    LIBRARIAN = "librarian"
    ADMIN = "admin"

    CHOICES = [
        (STUDENT, "Student"),
        (LIBRARIAN, "Librarian"),
        (ADMIN, "Admin"),
    ]


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role=UserRoles.STUDENT, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """ Creates an Admin user """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, role=UserRoles.ADMIN, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=UserRoles.CHOICES, default=UserRoles.STUDENT)
    dues = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",
        blank=True
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        blank=True
    )

    objects = UserManager()

    def is_student(self):
        return self.role == UserRoles.STUDENT

    def is_librarian(self):
        return self.role == UserRoles.LIBRARIAN

    def is_admin(self):
        return self.role == UserRoles.ADMIN

    def __str__(self):
        return f"{self.username} ({self.role})"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    borrow_limit = models.IntegerField(default=5)
    library_card_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    is_banned = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        """ Ensure the user is always a student when creating a Student instance """
        self.user.role = UserRoles.STUDENT
        self.user.save()
        super().save(*args, **kwargs)


class Librarian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def save(self, *args, **kwargs):
        """ Ensure the user is always a librarian when creating a Librarian instance """
        self.user.role = UserRoles.LIBRARIAN
        self.user.save()
        super().save(*args, **kwargs)

    def add_book(self, title, authors, publisher, pages, price, genre, topics, available_copies):
        if not self.user.is_librarian():
            raise PermissionError("Only librarians can add books.")
        book = Book.create_book(
            title=title,
            authors=authors,
            publisher=publisher,
            pages=pages,
            price=price,
            genre=genre,
            topics=topics,
            available_copies=available_copies
        )
        return book

    def add_journal(self, title, authors, publisher, journal_type, publication_date, available_copies, issn=None):
        if not self.user.is_librarian():
            raise PermissionError("Only librarians can add journals.")
        journal = Journal.objects.create(
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
        return f"Librarian: {self.user.username}"


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    can_manage_dues = models.BooleanField(default=True)
    can_ban_users = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """ Ensure the user is always an admin when creating an Admin instance """
        self.user.role = UserRoles.ADMIN
        self.user.save()
        super().save(*args, **kwargs)

    def ban_student(self, student):
        if not self.can_ban_users:
            raise PermissionError("This admin does not have permission to ban students.")
        student.is_banned = True
        student.save()

    def __str__(self):
        return f"Admin: {self.user.username}"


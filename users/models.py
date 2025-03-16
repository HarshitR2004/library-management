from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission
from django.contrib.contenttypes.models import ContentType
from books.models import Book, Journal


# UserRoles
class UserRoles:
    STUDENT = "student"
    LIBRARIAN = "librarian"
    ADMIN = "admin"

    CHOICES = [
        (STUDENT, "Student"),
        (LIBRARIAN, "Librarian"),
        (ADMIN, "Admin"),
    ]


# UserManager Implementation
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role=UserRoles.STUDENT, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        extra_fields.setdefault("role", role)

        user = self.model(username=username, email=email, **extra_fields)  
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("role", UserRoles.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, email, password, **extra_fields)


# Custom User Model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=UserRoles.CHOICES, default=UserRoles.STUDENT)

    objects = UserManager()

    def is_student(self):
        return self.role == UserRoles.STUDENT

    def is_librarian(self):
        return self.role == UserRoles.LIBRARIAN

    def is_admin(self):
        return self.role == UserRoles.ADMIN

    def __str__(self):
        return f"{self.username} ({self.role})"


# Student Model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    borrow_limit = models.IntegerField(default=5)
    library_card_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    is_banned = models.BooleanField(default=False)
    dues = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        """ Ensure the user is always a student when creating a Student instance """
        self.user.role = UserRoles.STUDENT
        self.user.save()
        super().save(*args, **kwargs)

    def can_borrow(self):
        """ Check if the student is banned or has unpaid dues """
        return not self.is_banned and self.dues == 0.00


# Librarian Model
class Librarian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    can_approve_borrow = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """ Ensure the user is always a librarian when creating a Librarian instance and assign permissions """
        self.user.role = UserRoles.LIBRARIAN
        self.user.save()
        super().save(*args, **kwargs)

    def add_book(self, title, authors, publisher, pages, price, genre, topics, available_copies):
        """ Only librarians can add books and journals """
        if not self.user.is_librarian():
            raise PermissionError("Only librarians can add books and journals.")
        book = Book.objects.create(
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

    def verify_borrow(self, borrow):
        """ Verify borrow requests (librarian verification) """
        if not self.can_approve_borrow:
            raise PermissionError("This librarian can't approve borrow requests.")
        borrow.librarian_approved = True
        borrow.save(update_fields=["librarian_approved"])

    def verify_return(self, return_request):
        """ Verify book returns """
        return_request.return_approved = True
        return_request.save(update_fields=["return_approved"])

    def manage_book_visibility(self, book, is_visible):
        """ Librarians can decide if a book is visible to students """
        book.is_visible = is_visible
        book.save()


# Admin Model
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    can_manage_dues = models.BooleanField(default=True)
    can_ban_users = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """ Ensure the user is always an admin when creating an Admin instance """
        self.user.role = UserRoles.ADMIN
        self.user.save()
        super().save(*args, **kwargs)

    def ban_student(self, student, duration_days=30):
        """ Admin can ban students for a specified duration """
        if not self.can_ban_users:
            raise PermissionError("This admin does not have permission to ban students.")
        student.is_banned = True
        student.save()
        

    def manage_dues(self, student, amount):
        """ Admin can modify a student's dues """
        if not self.can_manage_dues:
            raise PermissionError("This admin does not have permission to manage dues.")
        student.dues += amount
        student.save()

    def __str__(self):
        return f"Admin: {self.user.username}"



from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


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
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=UserRoles.CHOICES, default=UserRoles.STUDENT)
    library_card_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    dues = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",  # Fixes the clash
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",  # Fixes the clash
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

class Librarian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"Librarian: {self.user.username}"

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    can_manage_dues = models.BooleanField(default=True)
    can_ban_users = models.BooleanField(default=True)

    def __str__(self):
        return f"Admin: {self.user.username}"

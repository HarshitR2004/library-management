import os
import django
from django.test import TestCase
from users.models import User, Student, Librarian, Admin

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elibrary.settings')
django.setup()

class UserTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username="student_1", email="student1@nitk.edu.in", password="test123")
        self.student1 = Student.objects.create(user=self.user1)

        self.user2 = User.objects.create_user(username="Librarian_2", email="librarian@nitk.edu.in", password="test123")
        self.librarian2 = Librarian.objects.create(user=self.user2)

        self.user3 = User.objects.create_user(username="Admin_2", email="admin@nitk.edu.in", password="test123")
        self.admin1 = Admin.objects.create(user=self.user3)

    def test_user_roles(self):
        self.assertTrue(hasattr(self.user1, "student"))
        self.assertTrue(hasattr(self.user2, "librarian"))
        self.assertTrue(hasattr(self.user3, "admin"))


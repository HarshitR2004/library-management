import os
import django
from django.test import TestCase
from users.models import User, Student, Librarian, Admin
from books.models import Author
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elibrary.settings')
django.setup()

# Base test setup to create shared test data
class BaseTestSetup(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Creates static test data for all test cases"""
        
        # Common Users
        cls.user_student = User.objects.create_user(username="student_1", email="student1@nitk.edu.in", password="test123")
        cls.student = Student.objects.create(user=cls.user_student)

        cls.user_librarian = User.objects.create_user(username="Librarian_2", email="librarian@nitk.edu.in", password="test123")
        cls.librarian = Librarian.objects.create(user=cls.user_librarian)

        cls.user_admin = User.objects.create_user(username="Admin_2", email="admin@nitk.edu.in", password="test123")
        cls.admin = Admin.objects.create(user=cls.user_admin)

        # Authors for books & journals
        cls.author1 = Author.objects.create(name="Author 1")
        cls.author2 = Author.objects.create(name="Author 2")

# Testing user creation
class UserTestCase(BaseTestSetup):
    
    def test_user_roles(self):
        self.assertTrue(self.student.user.is_student(), "Student role check failed")
        self.assertTrue(self.librarian.user.is_librarian(), "Librarian role check failed")
        self.assertTrue(self.admin.user.is_admin(), "Admin role check failed")

# Testing Librarian Functions
class TestLibrarian(BaseTestSetup):

    def test_add_book(self):
        book = self.librarian.add_book(
            title="Test Book",
            authors=[self.author1, self.author2],
            publisher="Test Publisher",
            pages=100,
            price=100.00,
            genre="Computer Science",
            topics="Test Topics",
            available_copies=10
        )

        self.assertIsNotNone(book, "Book creation failed")
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.publisher, "Test Publisher")
        self.assertEqual(book.pages, 100)
        self.assertEqual(book.price, 100.00)
        self.assertEqual(book.genre, "Computer Science")
        self.assertEqual(book.topics, "Test Topics")
        self.assertEqual(book.available_copies, 10)
        self.assertIn(self.author1, book.authors.all())
        self.assertIn(self.author2, book.authors.all())

    def test_add_journal(self):
        """Tests librarian adding a journal"""
        publication_date = datetime.strptime("2025-03-14", "%Y-%m-%d").date()
        journal = self.librarian.add_journal(
            title="Test Journal",
            authors=[self.author1, self.author2],
            publisher="Test Publisher",
            journal_type="Journal",
            publication_date=publication_date,
            available_copies=5,
            issn="1234-5678"
        )

        self.assertIsNotNone(journal, "Journal creation failed")
        self.assertEqual(journal.title, "Test Journal")
        self.assertEqual(journal.publisher, "Test Publisher")
        self.assertEqual(journal.journal_type, "Journal")
        self.assertEqual(journal.publication_date, publication_date)
        self.assertEqual(journal.available_copies, 5)
        self.assertEqual(journal.issn, "1234-5678")
        self.assertIn(self.author1, journal.authors.all())
        self.assertIn(self.author2, journal.authors.all())

# Testing Admin Functions
class TestAdmin(BaseTestSetup):
    """Tests admin actions"""

    def test_ban_student(self):
        """Tests banning a student"""
        self.admin.ban_student(self.student)
        self.assertTrue(self.student.is_banned, "Student ban failed")



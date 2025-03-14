import os
import django
from django.test import TestCase
from users.models import User, Student, Librarian, Admin
from books.models import Author
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elibrary.settings')
django.setup()

class UserTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test users once for all tests
        cls.user1 = User.objects.create_user(username="student_1", email="student1@nitk.edu.in", password="test123")
        cls.student1 = Student.objects.create(user=cls.user1)

        cls.user2 = User.objects.create_user(username="Librarian_2", email="librarian@nitk.edu.in", password="test123")
        cls.librarian2 = Librarian.objects.create(user=cls.user2)

        cls.user3 = User.objects.create_user(username="Admin_2", email="admin@nitk.edu.in", password="test123")
        cls.admin1 = Admin.objects.create(user=cls.user3)

    def test_user_roles(self):
        self.assertTrue(self.user1.is_student())
        self.assertTrue(self.user2.is_librarian())
        self.assertTrue(self.user3.is_admin())

class LibrarianPrivilegesTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a librarian user
        cls.user2 = User.objects.create_user(username="Librarian_2", email="librarian@nitk.edu.in", password="test123")
        cls.librarian2 = Librarian.objects.create(user=cls.user2)

        # Create authors
        cls.author1 = Author.objects.create(name="Author 1")
        cls.author2 = Author.objects.create(name="Author 2")

    def test_add_book(self):
        # Add a book using the librarian
        book = self.librarian2.add_book(
            title="Test Book",
            author=[self.author1, self.author2],
            publisher="Test Publisher",
            pages=100,
            price=100.00,
            genre="Computer Science",
            topics="Test Topics",
            available_copies=10
        )
        self.assertIsNotNone(book)
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.publisher, "Test Publisher")
        self.assertEqual(book.pages, 100)
        self.assertEqual(book.price, 100.00)
        self.assertEqual(book.genre, "Computer Science")
        self.assertEqual(book.topics, "Test Topics")
        self.assertEqual(book.available_copies, 10)
        self.assertIn(self.author1, book.author.all())
        self.assertIn(self.author2, book.author.all())

    def test_add_journal(self):
        # Add a journal using the librarian
        publication_date = datetime.strptime("2025-03-14", "%Y-%m-%d").date()
        journal = self.librarian2.add_journal(
            title="Test Journal",
            authors=[self.author1, self.author2],
            publisher="Test Publisher",
            journal_type="Journal",
            publication_date=publication_date,
            available_copies=5,
            issn="1234-5678"
        )
        self.assertIsNotNone(journal)
        self.assertEqual(journal.title, "Test Journal")
        self.assertEqual(journal.publisher, "Test Publisher")
        self.assertEqual(journal.journal_type, "Journal")
        self.assertEqual(journal.publication_date, publication_date)
        self.assertEqual(journal.available_copies, 5)
        self.assertEqual(journal.issn, "1234-5678")
        self.assertIn(self.author1, journal.authors.all())
        self.assertIn(self.author2, journal.authors.all())

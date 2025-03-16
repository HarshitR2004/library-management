import django
import os
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timedelta, datetime
from borrowing.models import Borrowing
from users.models import User, Student, Librarian, Admin
from books.models import Book, Journal, Author

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elibrary.settings')
django.setup()

class BaseTestSetup(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1_student = User.objects.create_user(
            username="student_1", 
            email="student1@nitk.edu.in", 
            password="test123"
        )
        cls.student1 = Student.objects.create(
            user=cls.user1_student,
            library_card_number="LC123456"
        )
        
        cls.user2_student = User.objects.create_user(
            username="student_2", 
            email="student2@nitk.edu.in", 
            password="test123"
        )
        cls.student2 = Student.objects.create(user=cls.user2_student)
        
        cls.user3_student = User.objects.create_user(
            username="student_3", 
            email="student3@nitk.edu.in", 
            password="test123"
        )
        cls.student3 = Student.objects.create(
            user=cls.user3_student,
            is_banned=True
        )
        
        cls.user_librarian = User.objects.create_user(
            username="Librarian_2", 
            email="librarian@nitk.edu.in", 
            password="test123"
        )
        cls.librarian = Librarian.objects.create(user=cls.user_librarian)
        
        cls.user_admin = User.objects.create_user(
            username="Admin_1", 
            email="admin@nitk.edu.in", 
            password="test123"
        )
        cls.admin = Admin.objects.create(user=cls.user_admin)
        
        cls.author1 = Author.objects.create(name="Author 1")
        cls.author2 = Author.objects.create(name="Author 2")
        
        cls.book = Book.create_book(
            title="Sample Book",
            authors=[cls.author1, cls.author2],
            publisher="Sample Publisher",
            pages=200,
            price=50.00,
            genre="Computer Science",
            topics="Sample Topics",
            available_copies=5
        )
        
        cls.journal = Journal.create_journal(
            title="Test Journal",
            authors=[cls.author1, cls.author2],
            publisher="Test Publisher",
            journal_type="Journal",
            publication_date=datetime.strptime("2025-03-14", "%Y-%m-%d").date(),
            available_copies=5,
            issn="1234-5678"
        )

class BorrowingTestCase(BaseTestSetup):
    def test_successful_book_borrowing_with_approval(self):
        """Test that a student with a valid library card can borrow a book after librarian approval."""
        borrowing = Borrowing.objects.create(user=self.user1_student, book=self.book)
        self.librarian.approve_borrow(borrowing)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 4)
        self.assertIsNotNone(borrowing.due_date)
        self.assertEqual(borrowing.due_date, borrowing.borrowed_at + timedelta(weeks=2))
    
    def test_borrowing_without_librarian_approval_fails(self):
        """Test that a book cannot be borrowed without librarian approval."""
        borrowing = Borrowing.objects.create(user=self.user1_student, book=self.book)
        with self.assertRaises(ValidationError):
            borrowing.clean()
    
    def test_prevent_double_borrowing(self):
        """Test that a user cannot borrow the same book twice before returning it."""
        borrowing = Borrowing.objects.create(user=self.user1_student, book=self.book)
        self.librarian.approve_borrow(borrowing)
        with self.assertRaises(ValidationError):
            second_borrowing = Borrowing.objects.create(user=self.user1_student, book=self.book)
            self.librarian.approve_borrow(second_borrowing)
            
            # TO DO: Writing a test for jouranl-admin approval 
    
    # def test_successful_journal_borrowing_with_admin_approval(self):
    #     """Test that a student can borrow a journal only with admin approval."""
    #     borrowing = Borrowing.objects.create(user=self.user1_student, journal=self.journal)
    #     self.admin.approve_borrow(borrowing)
    #     self.librarian.approve_borrow(borrowing)
    #     self.journal.refresh_from_db()
    #     self.assertEqual(self.journal.available_copies, 4)
    
    # def test_borrowing_journal_without_admin_approval_fails(self):
    #     """Test that borrowing a journal requires admin approval."""
    #     with self.assertRaises(ValidationError):
    #         borrowing = Borrowing.objects.create(user=self.user1_student, journal=self.journal)
    #         self.librarian.approve_borrow(borrowing)
    
    def test_returning_a_book(self):
        """Test that returning a borrowed book restores available copies."""
        borrowing = Borrowing.objects.create(user=self.user1_student, book=self.book)
        self.librarian.approve_borrow(borrowing)
        borrowing.return_item()
        self.book.refresh_from_db()
        self.assertIsNotNone(borrowing.returned_at)
        self.assertEqual(self.book.available_copies, 5)
    
    def test_borrowing_fails_for_banned_students(self):
        """Test that a banned student cannot borrow books."""
        with self.assertRaises(ValidationError):
            Borrowing.objects.create(user=self.user3_student, book=self.book)




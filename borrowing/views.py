from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Borrowing
from books.models import Book, Journal
from users.models import UserRoles, Librarian, User
from .serializers import BorrowingSerializer
from django.contrib.auth.models import Group
from django.utils  import timezone

# Custom permissions
class IsLibrarian(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Librarian').exists()

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Admin').exists()

class BorrowBookView(generics.CreateAPIView):
    """API to borrow a book or journal."""
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Check if user has a library card
        if not self.request.user.library_card_number:
            raise permissions.PermissionDenied("You need a verified library card to borrow items.")
        
        # Check if user is banned from borrowing
        if hasattr(self.request.user, 'is_banned') and self.request.user.is_banned:
            raise permissions.PermissionDenied("You are currently banned from borrowing items.")
            
        serializer.save(user=self.request.user)

class ReturnBookView(generics.UpdateAPIView):
    """API to return a borrowed book or journal."""
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]
    queryset = Borrowing.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if the user is returning their own borrowed item or is a librarian/admin
        if (instance.user != request.user and 
            not request.user.groups.filter(name__in=['Librarian', 'Admin']).exists()):
            return Response(
                {"error": "You can only return your own borrowed items."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        if instance.returned_at:
            return Response({"error": "Item already returned"}, status=status.HTTP_400_BAD_REQUEST)

        # If user is a librarian or admin, mark the return as verified
        if request.user.groups.filter(name__in=['Librarian', 'Admin']).exists():
            instance.librarian_verified = True
            
        instance.return_item()
        return Response({"message": "Item returned successfully"}, status=status.HTTP_200_OK)

class BorrowingListView(generics.ListAPIView):
    """API to list user's borrowed books."""
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # If user is librarian or admin, show all borrowings
        if self.request.user.groups.filter(name__in=['Librarian', 'Admin']).exists():
            return Borrowing.objects.all()
        # Otherwise, show only the user's borrowings
        return Borrowing.objects.filter(user=self.request.user)

# New views for librarian and admin functionality
class VerifyBorrowingView(generics.UpdateAPIView):
    """API for librarians to verify borrowings."""
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated, IsLibrarian|IsAdmin]
    queryset = Borrowing.objects.all()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.librarian_verified = True
        instance.save()
        return Response({"message": "Borrowing verified successfully"}, status=status.HTTP_200_OK)

class BanUserView(generics.UpdateAPIView):
    """API for admins to ban users from borrowing."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def update(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        ban_days = request.data.get('ban_days', 10)  # Default ban of 10 days
        
        try:
            user = User.objects.get(id=user_id)
            user.is_banned = True
            user.ban_until = timezone.now() + timezone.timedelta(days=ban_days)
            user.save()
            return Response({"message": f"User banned for {ban_days} days"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@login_required
def view_books(request):
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.user.role == UserRoles.STUDENT and not request.user.library_card_number:
        return HttpResponseForbidden("You need a verified issue card to borrow books.")
    
    if request.method == "POST":
        borrowing = Borrowing(user=request.user, book=book, due_date=request.POST['due_date'])
        try:
            borrowing.save()
            return redirect('view_books')
        except ValueError as e:
            return render(request, 'books/book_detail.html', {'book': book, 'error': str(e)})
    
    return render(request, 'books/book_detail.html', {'book': book})

@login_required
def return_book(request, borrowing_id):
    borrowing = get_object_or_404(Borrowing, id=borrowing_id)
    if request.user.role == UserRoles.STUDENT and borrowing.user != request.user:
        return HttpResponseForbidden("You can only return books you have borrowed.")
    
    borrowing.return_item()
    return redirect('view_books')

@login_required
def manage_books(request):
    if request.user.role != UserRoles.LIBRARIAN:
        return HttpResponseForbidden("Only librarians can manage books.")
    
    books = Book.objects.all()
    return render(request, 'books/manage_books.html', {'books': books})

@login_required
def add_book(request):
    if request.user.role != UserRoles.LIBRARIAN:
        return HttpResponseForbidden("Only librarians can add books.")
    
    if request.method == "POST":
        title = request.POST['title']
        author = request.POST.getlist('author')
        publisher = request.POST['publisher']
        pages = request.POST['pages']
        price = request.POST['price']
        genre = request.POST['genre']
        topics = request.POST['topics']
        available_copies = request.POST['available_copies']
        
        librarian = Librarian.objects.get(user=request.user)
        librarian.add_book(title, author, publisher, pages, price, genre, topics, available_copies)
        return redirect('manage_books')
    
    return render(request, 'books/add_book.html')

@login_required
def add_journal(request):
    if request.user.role != UserRoles.LIBRARIAN:
        return HttpResponseForbidden("Only librarians can add journals.")
    
    if request.method == "POST":
        title = request.POST['title']
        authors = request.POST.getlist('authors')
        publisher = request.POST['publisher']
        journal_type = request.POST['journal_type']
        publication_date = request.POST['publication_date']
        available_copies = request.POST['available_copies']
        issn = request.POST['issn']
        
        librarian = Librarian.objects.get(user=request.user)
        librarian.add_journal(title, authors, publisher, journal_type, publication_date, available_copies, issn)
        return redirect('manage_books')
    
    return render(request, 'books/add_journal.html')



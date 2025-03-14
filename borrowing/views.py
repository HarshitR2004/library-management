from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Borrowing
from books.models import Book, Journal
from .serializers import BorrowingSerializer
from django.contrib.auth.models import Group

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
        ban_days = request.data.get('ban_days', 30)  # Default 30 days
        
        try:
            user = User.objects.get(id=user_id)
            user.is_banned = True
            user.ban_until = timezone.now() + timezone.timedelta(days=ban_days)
            user.save()
            return Response({"message": f"User banned for {ban_days} days"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    

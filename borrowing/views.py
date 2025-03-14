from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Borrowing
from books.models import Book, Journal
from .serializers import BorrowingSerializer


class BorrowBookView(generics.CreateAPIView):
    """API to borrow a book or journal."""
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReturnBookView(generics.UpdateAPIView):
    """API to return a borrowed book or journal."""
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]
    queryset = Borrowing.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.returned_at:
            return Response({"error": "Item already returned"}, status=status.HTTP_400_BAD_REQUEST)

        instance.return_item()
        return Response({"message": "Item returned successfully"}, status=status.HTTP_200_OK)

class BorrowingListView(generics.ListAPIView):
    """API to list user's borrowed books."""
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Borrowing.objects.filter(user=self.request.user)
    
    

from rest_framework import serializers
from .models import Borrowing

class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = '__all__'
        read_only_fields = ['borrowed_at', 'returned_at']

    def validate(self, data):
        """Enforce borrowing rules."""
        user = data.get("user")
        book = data.get("book", None)
        journal = data.get("journal", None)

        if book and journal:
            raise serializers.ValidationError("You can only borrow either a book or a journal at a time.")

        if book and book.available_copies <= 0:
            raise serializers.ValidationError(f"No copies available for '{book.title}'.")

        if journal and journal.available_copies <= 0:
            raise serializers.ValidationError(f"No copies available for '{journal.title}'.")

        if journal and not data.get("faculty_approved"):
            raise serializers.ValidationError("Faculty approval is required for journals/magazines.")

        # Borrowing limit (e.g., max 5 books)
        if user.borrowing_set.filter(returned_at__isnull=True).count() >= 5:
            raise serializers.ValidationError("Borrowing limit reached. Return books first.")

        return data

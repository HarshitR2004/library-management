from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    authors = forms.CharField(
        max_length=500,
        required=True,
        help_text="Enter author names separated by commas."
    )

    class Meta:
        model = Book
        fields = ["title", "publisher", "pages", "price", "genre", "topics", "available_copies", "authors"]

    def clean_authors(self):
        """Splits the input authors string into a list."""
        authors_str = self.cleaned_data.get("authors", "")
        return [name.strip() for name in authors_str.split(",") if name.strip()]








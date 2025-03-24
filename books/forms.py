from django import forms
from .models import Author, Book

class AdditionForm(forms.ModelForm):
    author = forms.CharField(
        max_length=255, 
        required=True, 
        help_text="Enter the author's name."
    )

    class Meta:
        model = Book 
        fields = ["title", "publisher", "available_copies", "author", "pages", "price", "genre", "topics"]

    def __init__(self, *args, **kwargs):
        model = kwargs.pop("model", None)
        super().__init__(*args, **kwargs)
        
        if model:
            self.Meta.model = model  

    def clean_author(self):
        """Ensure the author exists or create a new one."""
        author_name = self.cleaned_data.get("author").strip()
        author, _ = Author.objects.get_or_create(name=author_name)
        return author  

    
class BookSearchForm(forms.Form):
    search = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title or topics...'
        })
    )
    
    genre = forms.ChoiceField(
        required=False,
        choices=[('', 'All Genres')] + Book.GenreChoices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    author = forms.ModelChoiceField(
        required=False,
        queryset=Author.objects.all(),
        empty_label="All Authors",
        widget=forms.Select(attrs={'class': 'form-select'})
    )







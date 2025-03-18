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

    








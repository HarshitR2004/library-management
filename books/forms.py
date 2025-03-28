from django import forms
from .models import Author, Book, Journal

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
        choices=lambda: [('', 'All Genres')] + list(Book.GenreChoices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    author_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by author name...'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].queryset = Author.objects.all()

class AdditionForm(forms.Form):
    """Dynamic form for adding both books and journals."""
    
    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    author_name = forms.CharField(
        max_length=255, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter author name'
        })
    )
    publisher = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    available_copies = forms.IntegerField(min_value=0, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    # Book fields
    pages = forms.IntegerField(min_value=1, required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    price = forms.DecimalField(max_digits=8, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    genre = forms.ChoiceField(choices=Book.GenreChoices, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    topics = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    
    # Journal fields
    journal_type = forms.ChoiceField(choices=Journal.JOURNAL_TYPE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    publication_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    issn = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', None)
        super().__init__(*args, **kwargs)
        
        if self.model == Book:
            self._set_book_fields_required()
        elif self.model == Journal:
            self._set_journal_fields_required()
    
    def _set_book_fields_required(self):
        """Make book-specific fields required"""
        self.fields['pages'].required = True
        self.fields['price'].required = True
        self.fields['genre'].required = True
        
        # journal-specific fields not required
        self.fields['journal_type'].required = False
        self.fields['publication_date'].required = False
        self.fields['issn'].required = False
    
    def _set_journal_fields_required(self):
        """Make journal-specific fields required"""
        self.fields['journal_type'].required = True
        self.fields['publication_date'].required = True
        
        # book-specific fields not required
        self.fields['pages'].required = False
        self.fields['price'].required = False
        self.fields['genre'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.model == Journal:
            journal_type = cleaned_data.get('journal_type')
            issn = cleaned_data.get('issn')
            
            if journal_type == 'Journal' and not issn:
                self.add_error('issn', 'ISSN is required for Journals.')
            elif journal_type != 'Journal' and issn:
                self.add_error('issn', 'ISSN should only be provided for Journals.')
        
        return cleaned_data
    
    def save(self):
        """Create and save a new book or journal instance with author."""
        author_name = self.cleaned_data['author_name']
        author, created = Author.objects.get_or_create(name=author_name)

        if self.model == Book:
            return Book.objects.create(
                title=self.cleaned_data['title'],
                author=author,  
                publisher=self.cleaned_data['publisher'],
                pages=self.cleaned_data['pages'],
                price=self.cleaned_data['price'],
                genre=self.cleaned_data['genre'],
                topics=self.cleaned_data['topics'],
                available_copies=self.cleaned_data['available_copies']
            )
        elif self.model == Journal:
            return Journal.objects.create(
                title=self.cleaned_data['title'],
                author=author,  
                publisher=self.cleaned_data['publisher'],
                journal_type=self.cleaned_data['journal_type'],
                publication_date=self.cleaned_data['publication_date'],
                issn=self.cleaned_data['issn'],
                available_copies=self.cleaned_data['available_copies']
            )







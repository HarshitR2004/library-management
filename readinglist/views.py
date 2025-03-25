from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import Student
from django.shortcuts import get_object_or_404, render
from .models import ReadingList
from books.models import Book

# Create your views here.
@login_required
def reading_list(request):
    """Display the reading list of the logged-in user."""
    reading_list_items = ReadingList.objects.filter(user=request.user)
    books = [item.book for item in reading_list_items]
    
    return render(request, 'reading_list.html', {'books': books})

@login_required
def add_to_reading_list(request, item_id):
    """Add a book or journal to the reading list."""
    user = request.user  
    item = get_object_or_404(Book, id=item_id)
    
    ReadingList.objects.create(book=item, user=user)
    
    return redirect('reading_list')

@login_required
def remove_from_reading_list(request, item_id):
    """Remove a book from the reading list."""
    user = request.user
    item = get_object_or_404(Book, id=item_id)
    
    ReadingList.objects.filter(book=item, user=user).delete()
    
    return redirect('reading_list')

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
from .models import Book
from .forms import BookForm

@login_required
def book_list(request):
    books = Book.objects.all() 
    return render(request, "books/book_list.html", {"books": books})

@login_required
def add_book(request):
    """Only admins and librarians can add books."""
    if not request.user.is_admin() and not request.user.is_librarian():
        return HttpResponseForbidden("You do not have permission to add books.")

    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("book_list")
    else:
        form = BookForm()
    
    return render(request, "books/add_book.html", {"form": form})

@login_required
def delete_book(request, book_id):
    """Only admins and librarians can delete books."""
    book = get_object_or_404(Book, id=book_id)
    if not request.user.is_admin() and not request.user.is_librarian():
        return HttpResponseForbidden("You do not have permission to delete books.")
    
    book.delete()
    return redirect("book_list")


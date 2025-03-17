from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
from .models import Book, BookAuthor, Author
from .forms import BookForm

@login_required
def book_list(request):
    books = Book.objects.all()
    if request.user.is_admin():
        return render(request, "admin_dashboard.html", {"books": books})
    elif request.user.is_librarian():
        return render(request, "librarian_dashboard.html", {"books": books})
    elif request.user.is_student():
        return render(request, "student_dashboard.html", {"books": books})
    else:
        return HttpResponseForbidden("You do not have permission to view this page.")
    
    
@login_required
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()  # Save the book first
            
            # Get the authors from input
            author_names = request.POST.get("authors", "").split(",")
            for name in author_names:
                name = name.strip()
                if name:
                    author, created = Author.objects.get_or_create(name=name)
                    BookAuthor.objects.create(book=book, author=author)  # Link authors to book

            return redirect("book_list")

    else:
        form = BookForm()

    return render(request, "add_book.html", {"form": form})

  
        
        
        
@login_required
def delete_book(request, book_id):
    """Only admins and librarians can delete books."""
    book = get_object_or_404(Book, id=book_id)
    if not request.user.is_admin() and not request.user.is_librarian():
        return HttpResponseForbidden("You do not have permission to delete books.")
    
    if request.method == "POST":
        book.delete()
        if request.user.is_admin():
            return redirect("admin_dashboard")
        elif request.user.is_librarian():
            return redirect("librarian_dashboard")
    
    return render(request, "confirm_delete_book.html", {"book": book})


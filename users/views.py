from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
from books.models import Book
from books.forms import AdditionForm


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_admin():
                return redirect("admin_dashboard")
            elif user.is_librarian():
                return redirect("librarian_dashboard")
            elif user.is_student():
                return redirect("student_dashboard")

            return redirect("/")

        return render(request, "login.html", {"error": "Invalid username or password"})  

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def admin_dashboard(request):
    books = Book.objects.all()
    return render(request, "admin_dashboard.html", {"books": books})

@login_required
def librarian_dashboard(request):
    books = Book.objects.all()
    return render(request, "librarian_dashboard.html", {"books": books})

@login_required
def student_dashboard(request):
    books = Book.objects.all()
    return render(request, "student_dashboard.html", {"books": books})

def add_book(request):
    """Only admins and librarians can add books."""
    if not request.user.is_admin() and not request.user.is_librarian():
        return HttpResponseForbidden("You do not have permission to add books.")

    if request.method == "POST":
        form = AdditionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("book_list")
    else:
        form = AdditionForm()
    
    return render(request, "add_book.html", {"form": form})

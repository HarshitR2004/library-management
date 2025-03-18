from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import Borrow
from users.models import Student
from books.models import Book

@login_required
def borrow_request(request, book_id):
    """Student requests to borrow a book (Pending status)."""
    if not request.user.is_student():
        messages.error(request, "Only students can borrow books.")
        return redirect("student_dashboard")

    student = get_object_or_404(Student, user=request.user)
    book = get_object_or_404(Book, id=book_id)

    existing_borrow = Borrow.objects.filter(student=student, is_returned=False).exclude(status="Rejected").exists()
    if existing_borrow:
        messages.error(request, "You already have a pending or borrowed book.")
        return redirect("student_dashboard")

    borrow_entry = Borrow.objects.create(student=student, book=book, status="Pending")
    messages.success(request, "Borrow request submitted. Wait for librarian approval.")
    
    return redirect("student_dashboard")

@login_required
def borrow_status(request):
    """Student checks the status of their borrow requests."""
    borrow_requests = Borrow.objects.filter(student__user=request.user)
    return render(request, "borrow_status.html", {"borrow_requests": borrow_requests})

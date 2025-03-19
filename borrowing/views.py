from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import Borrow
from users.models import Student
from books.models import Book


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

def borrow_status(request):
    """Student checks the status of their borrow requests."""
    borrow_requests = Borrow.objects.filter(student__user=request.user)
    return render(request, "borrow_status.html", {"borrow_requests": borrow_requests})

def manage_status(request):
    """Libarian can manage the status of the borrow requests"""
    if not request.user.is_libarian:
        messages.error(request, "Only Librarians can manage borrow status")
        
    approval_status = get_object_or_404(Borrow, user = request.user)
    
    if approval_status.status != "Pending":
        messages.error(request, "Request already processed")
    
    
    
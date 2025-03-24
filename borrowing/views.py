from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Borrow
from users.models import Student, Librarian
from books.models import Book


@login_required
def borrow_request(request, book_id):
    """Student requests to borrow a book."""
    
    student = get_object_or_404(Student, user=request.user)
    book = get_object_or_404(Book, id=book_id)

    # Check if the student has already borrowed this specific book
    existing_borrow = Borrow.objects.filter(
        student=student, 
        book=book,
        is_returned=False
    ).exclude(status="Rejected").exists()
    
    if existing_borrow:
        return redirect("student_dashboard")

    # Check if student has reached their borrow limit
    active_borrows_count = Borrow.objects.filter(
        student=student,
        is_returned=False
    ).exclude(status="Rejected").count()
    
    if active_borrows_count >= student.borrow_limit:
        return redirect("student_dashboard")

    borrow_entry = Borrow.objects.create(student=student, book=book, status="Pending")
    
    return redirect("student_dashboard")



@login_required
def borrow_status(request):
    """Student checks the status of their borrow requests."""
    if not hasattr(request.user, "student"):
        return redirect("login")

    borrow_requests = Borrow.objects.filter(student__user=request.user)
    return render(request, "borrow_status.html", {"borrow_requests": borrow_requests})

@login_required
def manage_borrow_requests(request):
    """View for librarians to see and manage all borrow requests."""
    if not hasattr(request.user, "librarian"):
        return redirect("librarian_dashboard")

    pending_requests = Borrow.objects.filter(status="Pending")
    approved_requests = Borrow.objects.filter(status="Approved")
    rejected_requests = Borrow.objects.filter(status="Rejected")
    pending_returns = Borrow.objects.filter(status="Pending Return")

    context = {
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
        "rejected_requests": rejected_requests,
        "pending_returns": pending_returns
    }
    return render(request, "manage_requests.html", context)

@login_required
def approve_borrow_request(request, borrow_id):
    """Handle librarian approval of borrow requests."""
    if not hasattr(request.user, "librarian"):
        messages.error(request, "Unauthorized access.")
        return redirect("librarian_dashboard")

    borrow_request = get_object_or_404(Borrow, id=borrow_id)

    
    borrow_request.approve()

    return redirect("manage-borrow-requests")

@login_required
def reject_borrow_request(request, borrow_id):
    """Handle librarian rejection of borrow requests."""
    if not hasattr(request.user, "librarian"):
        return redirect("librarian_dashboard")

    borrow_request = get_object_or_404(Borrow, id=borrow_id)
    
    borrow_request.reject()

    return redirect("manage-borrow-requests")


@login_required
def request_return_book(request, borrow_id):
    """Allows a user to request a return. Librarian will approve later."""
    student = get_object_or_404(Student, user = request.user)
    borrow = get_object_or_404(Borrow, id=borrow_id, status = "Approved")

    borrow.status = 'Pending Return'
    borrow.save()
    return redirect('borrow_status')

@login_required
def approve_return(request, borrow_id):
    """Librarian approves the book return."""
    if not hasattr(request.user, "librarian"):
        return redirect('dashboard')
    
    borrow = get_object_or_404(Borrow, id=borrow_id, status= "Pending Return")
    borrow.return_book()
    return redirect('manage-returns')

@login_required
def manage_returns(request):
    """View for librarians to manage book returns."""
    if not hasattr(request.user, "librarian"):
        messages.error(request, "Only librarians can access this page.")
        return redirect("librarian_dashboard")

    pending_returns = Borrow.objects.filter(status="Pending Return") 

    context = {"pending_returns": pending_returns}
    return render(request, "manage_returns.html", context)
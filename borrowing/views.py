from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Borrow
from users.models import Student
from books.models import Book, Journal


@login_required
def borrow_request(request):
    """Create a borrow request for a book or journal."""
    if not request.user.is_student():
        return HttpResponseForbidden("Only students can borrow items.")
        
    item_type = request.GET.get('item_type')
    item_id = request.GET.get('item_id')
    
    if item_type not in ['book', 'journal']:
        return HttpResponseBadRequest("Invalid item type.")
        
    student = get_object_or_404(Student, user=request.user)
    
    if student.borrow_limit <= 0:
        messages.error(request, "You have reached your borrowing limit.")
        return redirect('student_dashboard')
    
    if item_type == 'book':
        item = get_object_or_404(Book, id=item_id)
        existing_borrow = Borrow.objects.filter(student=student, book=item, is_returned=False).exists()
    else:  
        item = get_object_or_404(Journal, id=item_id)
        if not item.is_approved:
            messages.error(request, "This journal has not been approved for borrowing yet.")
            return redirect('journal_list')
        existing_borrow = Borrow.objects.filter(student=student, journal=item, is_returned=False).exists()
    
    if existing_borrow:
        messages.info(request, f"You already have a pending borrow request for this {item_type}.")
        return redirect(f"{item_type}_list")
        
    if item.available_copies <= 0:
        messages.error(request, f"No copies of this {item_type} are available.")
        return redirect(f"{item_type}_list")
        
    borrow_kwargs = {
        'student': student,
        f'{item_type}': item,
        'status': 'Pending',
    }
    
    borrow = Borrow.objects.create(**borrow_kwargs)
    
    messages.success(request, f"Borrow request for '{item.title}' has been submitted.")
    return redirect('borrow_status')


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
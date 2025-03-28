from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.core.exceptions import ValidationError
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
    
    active_statuses = ['Pending', 'Approved']
    
    if item_type == 'book':
        item = get_object_or_404(Book, id=item_id)
        existing_borrow = Borrow.objects.filter(
            student=student, 
            book=item, 
            status__in=active_statuses
        ).exists()
    else:  
        item = get_object_or_404(Journal, id=item_id)
        if not item.is_approved:
            return redirect('journal_list')
        existing_borrow = Borrow.objects.filter(
            student=student, 
            journal=item, 
            status__in=active_statuses
        ).exists()
    
    if existing_borrow:
        return redirect(f"{item_type}_list")
    
    try:
        borrow_kwargs = {
            'student': student,
            f'{item_type}': item,
            'status': 'Pending'
        }
        borrow = Borrow.objects.create(**borrow_kwargs)
        
    except ValidationError as e:
        return redirect(f"{item_type}_list")
        
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
    if not request.user.is_librarian:
        return HttpResponseForbidden("Only librarians can approve requests.")

    borrow = get_object_or_404(Borrow, id=borrow_id, status='Pending')
    
    try:
        borrow.approve()
    except Exception as e:
        HttpResponseBadRequest("Error approving request: {str(e)}")
    
    return redirect('manage-borrow-requests')

@login_required
def reject_borrow_request(request, borrow_id):
    """Handle librarian rejection of borrow requests."""
    if not request.user.is_librarian:
        return HttpResponseForbidden("Only librarians can reject requests.")

    borrow = get_object_or_404(Borrow, id=borrow_id, status='Pending')
    
    try:
        borrow.reject()
    except Exception as e:
        HttpResponseBadRequest("Error rejecting request: {str(e)}")
    
    return redirect('manage-borrow-requests')

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

# Change the return_book method from:
def return_book(self):
    if self.status == 'Returned':
        raise ValueError("This item has already been returned.")
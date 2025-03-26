from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Due, Payment
from users.models import Student

@login_required
def student_dues(request):
    """Show all dues for the logged in student."""
    student = get_object_or_404(Student, user=request.user)
    dues = Due.objects.filter(borrow__student=student).select_related('borrow')
    
    for due in dues:
        due.update_fine()
    
    context = {
        'dues': dues,
        'total_unpaid': sum(due.amount for due in dues if not due.is_paid),
    }
    
    return render(request, 'student_dues.html', context)

# Librarian views
@login_required
def librarian_dues_dashboard(request):
    """Show all dues - only for librarians."""
    if not request.user.is_librarian:
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    dues = Due.objects.all().select_related('borrow__student__user')
    
    for due in dues:
        due.update_fine()
    
    paid_dues = [due for due in dues if due.is_paid]
    unpaid_dues = [due for due in dues if not due.is_paid]
    
    context = {
        'dues': dues,
        'paid_dues': paid_dues,
        'unpaid_dues': unpaid_dues,
        'total_collected': sum(due.amount for due in paid_dues),
        'total_pending': sum(due.amount for due in unpaid_dues),
    }
    
    return render(request, 'librarian_dues.html', context)

@login_required
@require_POST
def record_manual_payment(request, due_id):
    """Record a manual payment - for librarians."""
    if not request.user.is_librarian():
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    due = get_object_or_404(Due, id=due_id)
    
    if due.is_paid:
        messages.warning(request, "This due is already paid")
        return redirect('librarian_dues_dashboard')
    
    try:
        payment = Payment.objects.create(
            due=due,
            amount_paid=due.amount,
            payment_reference=f"MANUAL-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            processed_by=request.user,
            status='successful',
            is_successful=True
        )
        
        due.is_paid = True
        due.save()
        
    except Exception as e:
    
        return redirect('librarian_dues_dashboard')

@login_required
def due_payments(request, due_id):
    """Show payment history for a due."""
    if not request.user.is_librarian:
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    due = get_object_or_404(Due, id=due_id)
    payments = Payment.objects.filter(due=due).order_by('-payment_date')
    
    return render(request, 'due_payments.html', {
        'due': due,
        'payments': payments
    })







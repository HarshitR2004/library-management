from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import Due, Payment
from borrowing.models import Borrow
from users.models import Student

@login_required
def student_dues(request):
    """Show all dues for the logged in student."""
    student = get_object_or_404(Student, user=request.user)
    
    # Get all dues for the student through the borrow relationship
    dues = Due.objects.filter(borrow__student=student).select_related('borrow')
    
    # Update fine amounts
    for due in dues:
        due.update_fine()
    
    context = {
        'dues': dues,
        'total_unpaid': sum(due.amount for due in dues if not due.is_paid),
    }
    
    return render(request, 'student_dues.html', context)

@login_required
def view_due_details(request, due_id):
    """Show details for a specific due."""
    student = get_object_or_404(Student, user=request.user)
    due = get_object_or_404(Due, id=due_id, borrow__student=student)
    
    # Get payment history
    payments = Payment.objects.filter(due=due).order_by('-payment_date')
    
    # Update fine amount
    due.update_fine()
    
    context = {
        'due': due,
        'payments': payments,
        'razorpay_key': settings.RAZORPAY_KEY if hasattr(settings, 'RAZORPAY_KEY') else None,
    }
    
    return render(request, 'due_details.html', context)

@login_required
def initiate_payment(request, due_id):
    """Initiate payment for a due."""
    student = get_object_or_404(Student, user=request.user)
    due = get_object_or_404(Due, id=due_id, borrow__student=student)
    
    # Check if already paid
    if due.is_paid:
        messages.info(request, "This due is already paid.")
        return redirect('student_dues')
    
    # Update fine amount before payment
    due.update_fine()
    
    # Create a new payment
    payment = Payment.objects.create(
        due=due,
        amount_paid=due.amount
    )
    
    try:
        # Create Razorpay order
        order_data = payment.create_razorpay_order()
        
        context = {
            'due': due,
            'payment': payment,
            'order_id': order_data['id'],
            'amount': int(due.amount * 100), 
            'currency': "INR",
            'razorpay_key': settings.RAZORPAY_KEY,
            'callback_url': request.build_absolute_uri(reverse('payment_callback')),
            'student_name': student.user.get_full_name() or student.user.username,
            'student_email': student.user.email,
        }
        
        return render(request, 'payment_page.html', context)
        
    except Exception as e:
        messages.error(request, f"Failed to create payment: {str(e)}")
        return redirect('view_due_details', due_id=due_id)

@csrf_exempt
@require_POST
def payment_callback(request):
    """Handle Razorpay callback after payment."""
    payment_id = request.POST.get('razorpay_payment_id', '')
    order_id = request.POST.get('razorpay_order_id', '')
    signature = request.POST.get('razorpay_signature', '')
    
    # Find the payment
    payment = get_object_or_404(Payment, razorpay_order_id=order_id)
    
    # Process the payment
    success = payment.complete_payment(payment_id, signature)
    
    if success:
        messages.success(request, f"Payment successful! Your payment of ₹{payment.amount_paid} has been processed. Thank you for clearing your dues.")
        return redirect('student_dues')
    else:
        messages.error(request, "Payment verification failed. Please contact the library if funds were deducted.")
        return redirect('student_dues')





# Librarian views
@login_required
def librarian_dues_dashboard(request):
    """Show all dues - only for librarians."""
    if not hasattr(request.user, 'is_librarian') or not request.user.is_librarian():
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    # Get dues statistics
    dues = Due.objects.all().select_related('borrow__student__user')
    
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
def send_due_reminder(request, due_id):
    """Send a reminder email for a specific due."""
    if not hasattr(request.user, 'is_librarian') or not request.user.is_librarian():
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    due = get_object_or_404(Due, id=due_id)
    
    if due.send_reminder_email():
        messages.success(request, f"Reminder sent to {due.student.user.email}")
    else:
        messages.error(request, "Failed to send reminder")
    
    return redirect('librarian_dues_dashboard')

@login_required
def due_payments(request, due_id):
    """Show all payments for a specific due - for librarians."""
    if not hasattr(request.user, 'is_librarian') or not request.user.is_librarian():
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    due = get_object_or_404(Due, id=due_id)
    payments = Payment.objects.filter(due=due).order_by('-payment_date')
    
    return render(request, 'due_payments.html', {
        'due': due,
        'payments': payments
    })

@login_required
@require_POST
def mark_due_as_paid(request, due_id):
    """Mark a due as paid manually - for librarians."""
    if not hasattr(request.user, 'is_librarian') or not request.user.is_librarian():
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    due = get_object_or_404(Due, id=due_id)
    
    if due.is_paid:
        messages.info(request, "This due is already marked as paid")
    else:
        due.is_paid = True
        due.save()
        
        # Create a manual payment record
        Payment.objects.create(
            due=due,
            amount_paid=due.amount,
            status='successful',
            is_successful=True,
            razorpay_order_id=f"MANUAL-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        messages.success(request, f"Due marked as paid: {due}")
    
    return redirect('librarian_dues_dashboard')







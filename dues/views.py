from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Due, Payment
from django.contrib import messages
import razorpay

client = razorpay.Client(auth=("RAZORPAY_KEY", "RAZORPAY_SECRET"))


@login_required
def student_dues(request):
    """View for students to see their pending and paid dues."""
    dues = Due.objects.filter(student=request.user)
    return render(request, "student_dues.html", {"dues": dues})

@login_required
def make_payment(request, due_id):
    """Process payment using Razorpay mock integration."""
    due = get_object_or_404(Due, id=due_id, student=request.user)
    if due.is_paid:
        messages.error(request, "This due is already paid.")
        return redirect("student_dues")
    order_data = client.order.create({
        "amount": int(due.amount * 100),  
        "currency": "INR",
        "payment_capture": "1"
    })
    due.is_paid = True
    due.save()
    return render(request, "payment_page.html", {"order_id": order_data["id"], "due": due})


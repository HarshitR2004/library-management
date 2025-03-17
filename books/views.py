from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
from .models import Book, Journal, Author
from django.forms import modelform_factory
from .forms import AdditionForm

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
def add_item(request, item_type):
    """Handles adding both Books and Journals dynamically."""
    
    if request.user.is_student():
        return HttpResponseForbidden("You do not have access to add new books.")
    
    model_map = {
        "book": Book,
        "journal": Journal
    }
    
    if item_type not in model_map:
        return redirect("home")  
    
    model = model_map[item_type]  

    if request.method == "POST":
        form = AdditionForm(request.POST, model=model)  
        if form.is_valid():
            form.save()
            return redirect(f"{item_type}_list")  
    else:
        form = AdditionForm(model=model) 

    return render(request, "add_book.html", {"form": form, "item_type": item_type})

       
@login_required
def delete_item(request, item_type, item_id):
    """Only admins and librarians can delete books or journals."""
    
    if request.user.is_student():
        return HttpResponseForbidden("You do not have acess to add new books")
    
    model_map = {
        "book": Book,
        "journal": Journal
    }
    
    if item_type not in model_map:
        return redirect("home") 

    model = model_map[item_type]
    item = get_object_or_404(model, id=item_id)

    if request.method == "POST":
        item.delete()
        if request.user.is_superuser:
            return redirect("admin_dashboard")
        elif getattr(request.user, "is_librarian", False):
            return redirect("librarian_dashboard")

    return render(request, "confirm_delete_item.html", {"item": item, "item_type": item_type})


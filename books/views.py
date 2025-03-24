from django.views.generic import ListView
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Book, Journal
from .forms import AdditionForm, BookSearchForm
from books.models import Author

class BookListView(ListView):
    model = Book
    context_object_name = "books"
    
    def get_queryset(self):
        queryset = Book.objects.all().select_related('author')
        
        search_query = self.request.GET.get('search', '')
        genre = self.request.GET.get('genre', '')
        author_id = self.request.GET.get('author', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(topics__icontains=search_query)
            )
        
        if genre:
            queryset = queryset.filter(genre=genre)
            
        if author_id and author_id.isdigit():
            queryset = queryset.filter(author_id=author_id)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genre_choices'] = Book.GenreChoices
        context['search_form'] = BookSearchForm(self.request.GET or None)
        context['authors'] = Author.objects.all()
        context['genre'] = self.request.GET.get('genre', '')
                
        context['current_params'] = '&'.join([
            f"{key}={value}" 
            for key, value in self.request.GET.items() 
            if key != 'page'
        ])
        if context['current_params']:
            context['current_params'] = '&' + context['current_params']
            
        return context
    
    def get_template_names(self):
        """Return different templates based on the user's role."""
        user = self.request.user
        if hasattr(user, "is_admin") and user.is_admin():
            return ["admin_dashboard.html"]
        elif hasattr(user, "is_librarian") and user.is_librarian():
            return ["librarian_dashboard.html"]
        elif hasattr(user, "is_student") and user.is_student():
            return ["student_dashboard.html"]
        else:
            return HttpResponseForbidden("You do not have permission to view this page.") 
    
    
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

       

def delete_item(request, item_type, item_id):
    """Only admins and librarians can delete books or journals."""
    
    if request.user.is_student():
        return HttpResponseForbidden("You do not have permission to add new books")
    
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




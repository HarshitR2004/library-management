from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect("dashboard")  # Redirect to the dashboard
        else:
            return render(request, "users/login.html", {"error": "Invalid username or password"})
    
    return render(request, "users/login.html")



@login_required
def dashboard(request):
    """Redirect users based on their role."""
    if request.user.is_admin:
        return redirect("admin_dashboard")
    elif request.user.is_librarian:
        return redirect("librarian_dashboard")
    else:
        return redirect("student_dashboard")

@login_required
def admin_dashboard(request):
    return render(request, "users\templates\admin_dashboard.html")

@login_required
def librarian_dashboard(request):
    return render(request, "users\templates\librarian_dashboard.html")

@login_required
def student_dashboard(request):
    return render(request, "users\templates\student_dashboard.html")

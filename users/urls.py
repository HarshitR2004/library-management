from django.urls import path
from .views import login_view, admin_dashboard, librarian_dashboard, student_dashboard

urlpatterns = [
    path('', login_view, name='login'),  # Set the root URL to the login view
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/librarian/', librarian_dashboard, name='librarian_dashboard'),
    path('dashboard/student/', student_dashboard, name='student_dashboard'),
]

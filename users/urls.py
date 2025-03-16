from django.urls import path
from .views import dashboard, admin_dashboard, librarian_dashboard, student_dashboard, login_view

urlpatterns = [
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/librarian/", librarian_dashboard, name="librarian_dashboard"),
    path("dashboard/student/", student_dashboard, name="student_dashboard"),
]

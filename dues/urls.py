from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_dues, name='student_dues'),
    path('librarian/', views.librarian_dues_dashboard, name='librarian_dues_dashboard'),
    path('librarian/due/<int:due_id>/payments/', views.due_payments, name='due_payments'),
    path('librarian/due/<int:due_id>/mark-paid/', views.record_manual_payment, name='mark_due_as_paid'),
]
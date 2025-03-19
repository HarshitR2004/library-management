from django.urls import path
from .views import borrow_request, borrow_status, manage_status


urlpatterns = [
    path('borrow/request/<int:book_id>/', borrow_request, name='borrow_request'),
    path('borrow/status/', borrow_status, name='borrow_status'),
    path('borrow/approval/', manage_status, name='borrow_status'),
]
from django.urls import path
from .views import book_list, add_book, delete_book

urlpatterns = [
    path('', book_list, name='book_list'),
    path('add/', add_book, name='add_book'),
    path('delete/<int:book_id>/', delete_book, name='delete_book'),
]

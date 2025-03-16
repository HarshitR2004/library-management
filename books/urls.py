from django.urls import path
from .views import book_list, add_book, delete_book

urlpatterns = [
    path("books/", book_list, name="book_list"),
    path("books/add/", add_book, name="add_book"),
    path("books/delete/<int:book_id>/", delete_book, name="delete_book"),
]

from django.urls import path
from .views import BorrowBookView, ReturnBookView, BorrowingListView

urlpatterns = [
    path("borrow/", BorrowBookView.as_view(), name="borrow-book"),
    path("return/<int:pk>/", ReturnBookView.as_view(), name="return-book"),
    path("borrowed/", BorrowingListView.as_view(), name="borrowed-books"),
]

from django.urls import path
from .views import BookListView, add_item, delete_item, JournalListView, approve_journal

urlpatterns = [
    path('', BookListView.as_view(), name='book_list'),
    path('journals/', JournalListView.as_view(), name='journal_list'),
    path('add/book/', add_item, {"item_type": "book"}, name='add_book'),
    path('add/journal/', add_item, {"item_type": "journal"}, name='add_journal'),
    path('delete/<str:item_type>/<int:item_id>/', delete_item, name='delete_item'),
    path('approve-journal/<int:journal_id>/', approve_journal, name='approve_journal'),
]


from django.urls import path
from .views import BookListView, add_item, delete_item

urlpatterns = [
    path('', BookListView.as_view(), name='book_list'),
    path('add/book/', add_item, {"item_type": "book"}, name='add_book'),

    # path('journals/', journal_list, name='journal_list'),
    path('add/journal/', add_item, {"item_type": "journal"}, name='add_journal'),

    path('delete/<str:item_type>/<int:item_id>/', delete_item, name='delete_item'),
]


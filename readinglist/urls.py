from django.urls import path
from . import views

urlpatterns = [
    path('view/', views.reading_list, name='reading_list'),
    path('add_to_reading_list/<int:item_id>/', views.add_to_reading_list, name='add_to_reading_list'),
    path('remove_from_reading_list/<int:item_id>/', views.remove_from_reading_list, name='remove_from_reading_list'),
]
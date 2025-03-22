from django.urls import path
from .views import student_dues, make_payment

urlpatterns = [
    path('dues/', student_dues, name='dues'),
    path('payments/', make_payment, name='payments'),
]
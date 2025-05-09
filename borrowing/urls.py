from django.urls import path
from .views import manage_borrow_requests, approve_borrow_request, reject_borrow_request, borrow_status,borrow_request, request_return_book,approve_return, manage_returns


urlpatterns = [
    path("request/", borrow_request, name="borrow_request"),
    
    path("status/", borrow_status, name="borrow_status"),
    
    path("manage/", manage_borrow_requests, name="manage-borrow-requests"),
    
    path("approve/<int:borrow_id>/", approve_borrow_request, name="approve-borrow-request"),
    
    path("reject/<int:borrow_id>/", reject_borrow_request, name="reject-borrow-request"),
    
    path('return-request/<int:borrow_id>/', request_return_book, name='request_return_book'),
    
    path('approve-return/<int:borrow_id>/', approve_return, name='approve_return'),
    
    path("manage-returns/", manage_returns, name="manage-returns"),
]
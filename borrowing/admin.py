from django.contrib import admin
from .models import Borrowing

# Register your models here.
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'journal', 'borrowed_at', 'due_date', 'returned_at', 'faculty_approved')
    list_filter = ('returned_at', 'faculty_approved')
    search_fields = ('user__username', 'book__title', 'journal__title')

# Missing registration line:
admin.site.register(Borrowing, BorrowingAdmin)
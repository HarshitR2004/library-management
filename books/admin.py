from django.contrib import admin
from .models import Book

class BookAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return request.user.is_admin() or request.user.is_librarian()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_admin() or request.user.is_librarian()

    def has_change_permission(self, request, obj=None):
        return request.user.is_admin() or request.user.is_librarian()

admin.site.register(Book, BookAdmin)

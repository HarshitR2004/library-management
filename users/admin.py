from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Librarian, Admin


# Register your models here.
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('User Role', {'fields': ('role',)}),
    )

admin.site.register(Student)
admin.site.register(Librarian)
admin.site.register(Admin)

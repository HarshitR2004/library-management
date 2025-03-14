from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserRoles


def assign_role_permissions(user):
    """ Assign permissions based on the user role. """
    if user.is_student():
        group, _ = Group.objects.get_or_create(name="Student")
        permissions = [
            "view_booksbook",
            "view_booksjournal",
            "add_borrowingborrowing",
            "change_borrowingborrowing",
        ]

    elif user.is_librarian():
        group, _ = Group.objects.get_or_create(name="Librarian")
        permissions = [
            "add_booksbook",
            "add_booksjournal",
            "change_booksbook",
            "change_booksjournal",
            "change_borrowingborrowing",
        ]

    elif user.is_admin():
        group, _ = Group.objects.get_or_create(name="Admin")
        permissions = [
            "add_usersuser",
            "change_usersuser",
            "delete_usersuser",
            "change_borrowingborrowing",
        ]

    else:
        return

    # Assign permissions to the group
    for perm in permissions:
        permission = Permission.objects.get(codename=perm)
        group.permissions.add(permission)

    # Assign the group to the user
    user.groups.add(group)

@receiver(post_save, sender=User)
def set_user_role_permissions(sender, instance, created, **kwargs):
    """ Assigns permissions when a new user is created. """
    if created:
        assign_role_permissions(instance)
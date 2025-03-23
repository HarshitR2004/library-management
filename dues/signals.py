from django.db.models.signals import post_save
from django.dispatch import receiver
from borrowing.models import Borrow
from .models import Due

@receiver(post_save, sender=Borrow)
def create_or_update_due(sender, instance, created, **kwargs):
    """
    Create or update a Due record when a Borrow is saved and is overdue
    """
    # Only proceed if the book is returned and overdue
    if instance.is_returned and instance.return_date and instance.due_date and instance.return_date > instance.due_date:
        # Create or update the Due record
        due, created = Due.objects.get_or_create(borrow=instance)
        due.update_fine()
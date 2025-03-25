from django import template
from readinglist.models import ReadingList

register = template.Library()

@register.filter
def is_in_reading_list(book, user):
    return ReadingList.objects.filter(book=book, user=user).exists()
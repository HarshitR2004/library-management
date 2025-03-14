import django
from django.test import TestCase
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elibrary.settings')
django.setup()

class TestAddBooks(TestCase):
    """Testing if Librarian can add books"""
    
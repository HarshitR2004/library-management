# Generated by Django 5.1.7 on 2025-03-28 12:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('borrowing', '0003_borrow_journal_alter_borrow_book'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='borrow',
            name='is_returned',
        ),
    ]

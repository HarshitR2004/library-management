# Generated by Django 5.1.7 on 2025-03-15 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_student_dues'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='dues',
        ),
        migrations.AddField(
            model_name='librarian',
            name='can_apprvve_borrow',
            field=models.BooleanField(default=True),
        ),
    ]

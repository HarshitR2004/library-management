# Generated by Django 5.1.7 on 2025-03-14 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_user_library_card_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='is_banned',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 5.1.7 on 2025-03-16 06:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_book_available_copies_journal_available_copies'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='available_copies',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='book',
            name='genre',
            field=models.CharField(choices=[('Metallurgy', 'METALLURGY'), ('Computer Science', 'CS'), ('ECE', 'ECE'), ('EEE', 'EEE'), ('Mechanical', 'MECHANICAL'), ('Civil', 'CIVIL'), ('AI', 'AI'), ('Data Science', 'DATA SCIENCE'), ('Mining', 'MINING'), ('IT', 'IT')], max_length=50),
        ),
        migrations.AlterField(
            model_name='journal',
            name='available_copies',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]

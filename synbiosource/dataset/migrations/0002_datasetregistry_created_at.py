# Generated by Django 5.0.2 on 2024-02-26 16:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasetregistry',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

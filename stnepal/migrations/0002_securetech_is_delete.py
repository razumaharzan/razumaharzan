# Generated by Django 5.0 on 2024-01-03 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stnepal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='securetech',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
    ]
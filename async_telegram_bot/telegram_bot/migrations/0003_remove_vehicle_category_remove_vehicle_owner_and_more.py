# Generated by Django 4.0.6 on 2022-07-25 22:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0002_vehicle_searchhistory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='category',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='owner',
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='production_year',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(2022), django.core.validators.MinValueValidator(1900)], verbose_name='year'),
        ),
    ]

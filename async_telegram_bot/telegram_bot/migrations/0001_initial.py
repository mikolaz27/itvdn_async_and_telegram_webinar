# Generated by Django 4.0.6 on 2022-07-25 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_update', models.DateTimeField(auto_now=True, null=True)),
                ('tg_id', models.IntegerField(db_index=True)),
                ('username', models.CharField(max_length=64, null=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('email', models.EmailField(max_length=120, null=True)),
                ('phone', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'tg_users',
            },
        ),
    ]
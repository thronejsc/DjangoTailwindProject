# Generated by Django 4.2.1 on 2023-06-26 15:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_myuser_is_staff_alter_myuser_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='is_staff',
        ),
    ]

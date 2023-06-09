# Generated by Django 4.2.1 on 2023-05-30 13:51

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_rename_schoolwork_document'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='uploaded_at',
        ),
        migrations.AlterField(
            model_name='document',
            name='file',
            field=app.models.DatabaseStorage(upload_to=''),
        ),
        migrations.AlterField(
            model_name='document',
            name='subject',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='document',
            name='year_level',
            field=models.IntegerField(),
        ),
    ]

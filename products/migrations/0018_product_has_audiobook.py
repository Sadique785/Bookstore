# Generated by Django 5.0 on 2024-01-08 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0017_ebook'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='has_audiobook',
            field=models.BooleanField(default=False),
        ),
    ]

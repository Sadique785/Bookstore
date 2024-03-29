# Generated by Django 5.0 on 2024-01-03 12:19

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('sub_slug', models.SlugField(blank=True, unique=True)),
                ('category_image', models.ImageField(upload_to='categories')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

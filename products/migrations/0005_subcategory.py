# Generated by Django 5.0 on 2024-01-03 14:28

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_delete_subcategory'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('subcategory_name', models.CharField(max_length=100)),
                ('sub_slug', models.SlugField(blank=True, unique=True)),
                ('category_image', models.ImageField(upload_to='categories')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category', to='products.category')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

# Generated by Django 5.0 on 2024-01-05 12:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_subcategory_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sub_category',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='products.subcategory'),
        ),
    ]

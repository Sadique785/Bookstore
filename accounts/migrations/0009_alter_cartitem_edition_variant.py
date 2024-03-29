# Generated by Django 5.0 on 2024-01-28 21:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_cartitem_product'),
        ('products', '0025_alter_product_edition_variant_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='edition_variant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='edition_variant', to='products.editionvariant'),
        ),
    ]

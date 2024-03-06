# Generated by Django 5.0 on 2024-02-19 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_rename_product_variant_orderitem_edition_variant_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_paid',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')], default='Processing', max_length=20),
        ),
    ]

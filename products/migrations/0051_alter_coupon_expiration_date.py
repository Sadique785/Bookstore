# Generated by Django 5.0 on 2024-07-21 13:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0050_remove_editionvariant_stock_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 21, 13, 32, 11, 976904, tzinfo=datetime.timezone.utc)),
        ),
    ]

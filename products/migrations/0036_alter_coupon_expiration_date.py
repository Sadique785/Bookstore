# Generated by Django 5.0 on 2024-02-14 14:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0035_alter_coupon_expiration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 14, 14, 28, 58, 257847, tzinfo=datetime.timezone.utc)),
        ),
    ]

# Generated by Django 5.0 on 2024-02-13 06:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0033_alter_coupon_expiration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 13, 6, 20, 13, 358493, tzinfo=datetime.timezone.utc)),
        ),
    ]

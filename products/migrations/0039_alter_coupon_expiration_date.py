# Generated by Django 5.0 on 2024-02-19 05:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0038_alter_coupon_expiration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 19, 5, 17, 19, 159733, tzinfo=datetime.timezone.utc)),
        ),
    ]

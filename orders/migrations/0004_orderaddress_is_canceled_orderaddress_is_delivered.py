# Generated by Django 5.0 on 2024-01-29 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderaddress',
            name='is_canceled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orderaddress',
            name='is_delivered',
            field=models.BooleanField(default=False),
        ),
    ]

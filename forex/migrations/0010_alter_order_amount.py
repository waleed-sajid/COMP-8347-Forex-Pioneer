# Generated by Django 4.2.7 on 2023-11-29 02:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forex", "0009_alter_order_amount"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="amount",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
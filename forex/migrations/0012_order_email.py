# Generated by Django 4.2.7 on 2023-11-29 06:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forex", "0011_remove_order_email_order_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="email",
            field=models.EmailField(default=1, max_length=254),
            preserve_default=False,
        ),
    ]

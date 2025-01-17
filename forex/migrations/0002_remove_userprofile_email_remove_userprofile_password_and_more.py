# Generated by Django 4.2.7 on 2023-11-21 04:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("forex", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="email",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="password",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="username",
        ),
        migrations.AddField(
            model_name="userprofile",
            name="user",
            field=models.OneToOneField(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]

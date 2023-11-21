# your_app_name/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class CryptoCurrency(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=10)
    price_usd = models.DecimalField(max_digits=20, decimal_places=10)

    # Add more fields as needed

    def __str__(self):
        return self.name


# class CustomUser(models.Model):
#     email = models.EmailField(unique=True)
#
#     def __str__(self):
#         return self.username

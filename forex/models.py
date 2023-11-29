# forexPioneer/models.py
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_or_photo = models.FileField(upload_to='user_profiles/', null=True, blank=True)

    # Add other fields as needed

    def __str__(self):
        return self.user.username if self.user else f'User Profile {self.pk}'


class PasswordResetRequest(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Define the validity period (e.g., 1 hour)
        validity_period = timezone.timedelta(hours=1)
        expiration_time = self.created_at + validity_period
        return timezone.now() <= expiration_time


class Order(models.Model):
    email = models.EmailField(max_length=254)
    paid = models.BooleanField(default=False)
    amount = models.FloatField(default=0)
    description = models.CharField(default=None, max_length=800)

    def __str__(self):
        return self.email

# your_app_name/models.py
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_or_photo = models.FileField(upload_to='user_profiles/', null=True, blank=True)
    username = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=128)

    # Add other fields as needed

    def __str__(self):
        return self.user.username if self.user else f'User Profile {self.pk}'

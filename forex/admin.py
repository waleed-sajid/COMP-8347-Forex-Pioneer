from django.contrib import admin
from .models import UserProfile, Order, PasswordResetRequest


admin.site.register(UserProfile)
admin.site.register(Order)
admin.site.register(PasswordResetRequest)

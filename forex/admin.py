from django.contrib import admin
from .models import Order

# Register your models here.
from .models import UserProfile

admin.site.register(UserProfile)

admin.site.register(Order)

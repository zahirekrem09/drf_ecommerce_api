from django.contrib import admin
from .models import CustomUser, ImageUpload, UserProfile, UserAddress


admin.site.register((CustomUser, ImageUpload, UserProfile, UserAddress,))

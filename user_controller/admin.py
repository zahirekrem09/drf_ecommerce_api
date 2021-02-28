from django.contrib import admin
from .models import CustomUser, ImageUpload


admin.site.register((CustomUser, ImageUpload, ))

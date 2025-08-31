from django.contrib import admin

# Register your models here.
from .models import UserRegistrationModel,ImageModel

admin.site.register(UserRegistrationModel)

admin.site.register(ImageModel)
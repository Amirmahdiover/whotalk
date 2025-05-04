from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
UserAdmin.fieldsets += (('اطلاعات اضافی', {'fields': ('name', 'image', 'online', 'phone_number')}),)
admin.site.register(User, UserAdmin)

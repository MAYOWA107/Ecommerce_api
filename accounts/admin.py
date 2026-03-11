from django.contrib import admin

from .models import CustomUser


from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "last_name")


admin.site.register(CustomUser, CustomUserAdmin)

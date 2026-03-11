from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff set to True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("superuser must have is_superuser set to True")

        return self.create_user(email=email, password=password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.CharField(max_length=100, unique=True)
    user = models.CharField(max_length=45)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_pic_url = models.URLField(blank=True, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username

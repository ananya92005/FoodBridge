from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    DONOR = "DONOR", "Donor"
    NGO = "NGO", "NGO"
    ADMIN = "ADMIN", "Admin"


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=UserRole.choices)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.role})"


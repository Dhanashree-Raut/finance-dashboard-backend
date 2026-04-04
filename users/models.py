from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        VIEWER     = 'viewer',     'Viewer'
        ANALYST    = 'analyst',    'Analyst'
        ADMIN      = 'admin',      'Admin'
        SUPERADMIN = 'superadmin', 'Super Admin'
        # COMMENT

    role      = models.CharField(max_length=12, choices=Role.choices, default=Role.VIEWER)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
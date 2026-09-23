from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('OWNER', 'Property Owner'),
        ('TENANT', 'Tenant'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='TENANT',
        help_text="Designates whether this user is a Property Owner or a Tenant."
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact phone number."
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        help_text="Profile picture (optional)."
    )
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="Short bio or introduction."
    )

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        full_name = self.get_full_name()
        if full_name:
            return f"{full_name} ({self.username}) - {self.get_role_display()}"
        return f"{self.username} - {self.get_role_display()}"

    @property
    def is_owner(self):
        return self.role == 'OWNER' or self.is_superuser

    @property
    def is_tenant(self):
        return self.role == 'TENANT' or self.is_superuser

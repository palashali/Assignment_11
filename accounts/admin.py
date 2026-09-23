from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Profile Info', {
            'fields': ('role', 'phone_number', 'profile_picture', 'bio'),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & Profile Info', {
            'fields': ('role', 'email', 'first_name', 'last_name', 'phone_number', 'bio'),
        }),
    )

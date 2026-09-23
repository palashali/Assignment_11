from django.contrib import admin
from .models import RentalRequest


@admin.register(RentalRequest)
class RentalRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'property', 'tenant', 'status', 'request_date', 'updated_at')
    list_filter = ('status', 'request_date')
    search_fields = ('property__title', 'tenant__username', 'tenant__email', 'message')
    readonly_fields = ('request_date', 'updated_at')
    ordering = ('-request_date',)

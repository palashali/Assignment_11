from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'property', 'tenant', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('property__title', 'tenant__username', 'comment')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

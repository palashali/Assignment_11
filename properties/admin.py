from django.contrib import admin
from django.utils.html import format_html
from .models import Property, Favorite


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'location', 'rent', 'bedrooms', 'bathrooms', 'is_available', 'owner', 'created_at', 'image_thumbnail')
    list_filter = ('property_type', 'is_available', 'bedrooms', 'bathrooms', 'created_at')
    search_fields = ('title', 'description', 'location', 'owner__username', 'owner__email')
    list_editable = ('is_available',)
    readonly_fields = ('created_at', 'updated_at', 'image_preview')

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="40" style="object-fit:cover; border-radius:4px;" />', obj.image.url)
        return "No Image"
    image_thumbnail.short_description = "Thumbnail"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:250px; border-radius:8px;" />', obj.image.url)
        return "No Image Uploaded"
    image_preview.short_description = "Image Preview"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'property__title')

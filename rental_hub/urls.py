"""
URL configuration for rental_hub project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from properties.views import property_list_view

# Custom error handlers
handler404 = 'rental_hub.views.custom_404_view'
handler403 = 'rental_hub.views.custom_403_view'
handler500 = 'rental_hub.views.custom_500_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', property_list_view, name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('properties/', include('properties.urls', namespace='properties')),
    path('rentals/', include('rentals.urls', namespace='rentals')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

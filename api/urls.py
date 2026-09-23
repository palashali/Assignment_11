from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, RentalRequestViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='api_properties')
router.register(r'requests', RentalRequestViewSet, basename='api_requests')
router.register(r'reviews', ReviewViewSet, basename='api_reviews')

urlpatterns = [
    path('', include(router.urls)),
]

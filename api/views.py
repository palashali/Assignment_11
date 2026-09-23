from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from properties.models import Property
from rentals.models import RentalRequest
from reviews.models import Review
from .serializers import PropertySerializer, RentalRequestSerializer, ReviewSerializer


class PropertyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Properties:
    - List and retrieve properties (Public)
    - Create/Update/Delete properties (Authenticated Owners only)
    - Search & Filter by location, property_type, rent
    """
    queryset = Property.objects.filter(is_available=True).select_related('owner').prefetch_related('reviews')
    serializer_class = PropertySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['rent', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        property_type = self.request.query_params.get('property_type')
        if property_type:
            qs = qs.filter(property_type=property_type)
        min_rent = self.request.query_params.get('min_rent')
        if min_rent:
            qs = qs.filter(rent__gte=min_rent)
        max_rent = self.request.query_params.get('max_rent')
        if max_rent:
            qs = qs.filter(rent__lte=max_rent)
        return qs


class RentalRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Rental Requests:
    - Tenants view their own requests and can create new requests.
    - Owners view requests received for their properties.
    """
    serializer_class = RentalRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_owner', False):
            return RentalRequest.objects.filter(property__owner=user).select_related('property', 'tenant')
        return RentalRequest.objects.filter(tenant=user).select_related('property', 'tenant')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user)


class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Reviews (Read-only list and detail).
    """
    queryset = Review.objects.all().select_related('tenant', 'property')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

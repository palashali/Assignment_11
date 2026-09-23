from rest_framework import serializers
from django.contrib.auth import get_user_model
from properties.models import Property, Favorite
from rentals.models import RentalRequest
from reviews.models import Review

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number']


class ReviewSerializer(serializers.ModelSerializer):
    tenant = UserSummarySerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'property', 'tenant', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'tenant', 'created_at']


class PropertySerializer(serializers.ModelSerializer):
    owner = UserSummarySerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'owner', 'title', 'description', 'property_type',
            'location', 'rent', 'bedrooms', 'bathrooms', 'image',
            'is_available', 'average_rating', 'total_reviews', 'reviews',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at', 'average_rating', 'total_reviews']


class RentalRequestSerializer(serializers.ModelSerializer):
    tenant = UserSummarySerializer(read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)

    class Meta:
        model = RentalRequest
        fields = [
            'id', 'property', 'property_title', 'tenant',
            'message', 'status', 'request_date', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'request_date', 'updated_at']

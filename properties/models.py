from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Property(models.Model):
    PROPERTY_TYPE_CHOICES = (
        ('APARTMENT', 'Apartment'),
        ('HOUSE', 'House'),
        ('ROOM', 'Room'),
        ('OFFICE', 'Office'),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties',
        help_text="The property owner who manages this listing."
    )
    title = models.CharField(
        max_length=200,
        help_text="Property listing headline or title."
    )
    description = models.TextField(
        help_text="Detailed description of the property, features, and lease terms."
    )
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPE_CHOICES,
        default='APARTMENT',
        help_text="Type of property."
    )
    location = models.CharField(
        max_length=255,
        help_text="City, neighborhood, or full address."
    )
    rent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Monthly rental price in USD / BDT."
    )
    bedrooms = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        help_text="Number of bedrooms (0 for studio/office)."
    )
    bathrooms = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Number of bathrooms."
    )
    image = models.ImageField(
        upload_to='property_images/',
        blank=True,
        null=True,
        help_text="Main photo of the property."
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Mark whether the property is currently available for rent."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.location} (${self.rent}/mo)"

    def get_absolute_url(self):
        return reverse('properties:property_detail', kwargs={'pk': self.pk})

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None

    @property
    def total_reviews(self):
        return self.reviews.count()


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} favorited {self.property.title}"

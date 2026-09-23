from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from properties.models import Property


class Review(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="The reviewed property."
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="The tenant submitting the review."
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars."
    )
    comment = models.TextField(
        help_text="Feedback or experience review for this property."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('property', 'tenant')

    def clean(self):
        super().clean()
        if self.property_id and self.tenant_id:
            # Check if tenant has an accepted rental request for this property
            from rentals.models import RentalRequest
            has_accepted_request = RentalRequest.objects.filter(
                property_id=self.property_id,
                tenant_id=self.tenant_id,
                status=RentalRequest.STATUS_ACCEPTED
            ).exists()

            if not has_accepted_request:
                raise ValidationError(
                    "You can only submit a review for a property if you have an accepted rental request."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review by {self.tenant.username} for {self.property.title} ({self.rating}/5)"

import builtins
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from properties.models import Property

py_property = builtins.property


class RentalRequest(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='rental_requests',
        help_text="The requested property."
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rental_requests',
        help_text="The tenant sending the request."
    )
    message = models.TextField(
        help_text="Message from tenant to property owner detailing move-in date, occupancy, or questions."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text="Current status of the rental request."
    )
    request_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-request_date']
        constraints = [
            models.UniqueConstraint(
                fields=['property', 'tenant'],
                condition=models.Q(status='PENDING'),
                name='unique_pending_request_per_tenant_property'
            )
        ]

    def clean(self):
        super().clean()
        if self.property_id and self.tenant_id:
            # Rule: Property owner cannot send rental request for their own property
            if self.property.owner_id == self.tenant_id:
                raise ValidationError("You cannot submit a rental request for your own property.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Request by {self.tenant.username} for {self.property.title} ({self.get_status_display()})"

    @py_property
    def is_pending(self):
        return self.status == self.STATUS_PENDING

    @py_property
    def is_accepted(self):
        return self.status == self.STATUS_ACCEPTED

    @py_property
    def is_rejected(self):
        return self.status == self.STATUS_REJECTED

    @py_property
    def is_cancelled(self):
        return self.status == self.STATUS_CANCELLED

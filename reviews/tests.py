from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from properties.models import Property
from rentals.models import RentalRequest
from reviews.models import Review

User = get_user_model()


class ReviewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username='review_owner',
            email='owner@test.com',
            password='password123',
            role='OWNER'
        )
        self.tenant_accepted = User.objects.create_user(
            username='accepted_tenant',
            email='accepted@test.com',
            password='password123',
            role='TENANT'
        )
        self.tenant_pending = User.objects.create_user(
            username='pending_tenant',
            email='pending@test.com',
            password='password123',
            role='TENANT'
        )

        self.prop = Property.objects.create(
            owner=self.owner,
            title='Sunny Studio Apartment',
            description='Bright studio',
            property_type='APARTMENT',
            location='City Center',
            rent=1200.00,
            bedrooms=1,
            bathrooms=1,
            is_available=True
        )

        # Rental requests
        self.req_accepted = RentalRequest.objects.create(
            property=self.prop,
            tenant=self.tenant_accepted,
            message='Accepted rental',
            status=RentalRequest.STATUS_ACCEPTED
        )
        self.req_pending = RentalRequest.objects.create(
            property=self.prop,
            tenant=self.tenant_pending,
            message='Pending rental',
            status=RentalRequest.STATUS_PENDING
        )

    def test_tenant_with_accepted_request_can_review(self):
        self.client.login(username='accepted_tenant', password='password123')
        response = self.client.post(reverse('reviews:add_review', kwargs={'property_id': self.prop.pk}), {
            'rating': 5,
            'comment': 'Amazing place to live, highly recommended!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(property=self.prop, tenant=self.tenant_accepted).exists())
        review = Review.objects.get(property=self.prop, tenant=self.tenant_accepted)
        self.assertEqual(review.rating, 5)

        # Check average rating
        self.assertEqual(self.prop.average_rating, 5.0)

    def test_tenant_with_pending_request_cannot_review(self):
        self.client.login(username='pending_tenant', password='password123')
        response = self.client.post(reverse('reviews:add_review', kwargs={'property_id': self.prop.pk}), {
            'rating': 4,
            'comment': 'Should not be allowed yet'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(property=self.prop, tenant=self.tenant_pending).exists())

    def test_tenant_cannot_review_same_property_twice(self):
        Review.objects.create(
            property=self.prop,
            tenant=self.tenant_accepted,
            rating=5,
            comment='First review'
        )

        self.client.login(username='accepted_tenant', password='password123')
        response = self.client.post(reverse('reviews:add_review', kwargs={'property_id': self.prop.pk}), {
            'rating': 3,
            'comment': 'Second duplicate review attempt'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.filter(property=self.prop, tenant=self.tenant_accepted).count(), 1)

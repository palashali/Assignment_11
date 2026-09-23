from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from properties.models import Property
from rentals.models import RentalRequest

User = get_user_model()


class ApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username='api_owner',
            email='api_owner@test.com',
            password='password123',
            role='OWNER'
        )
        self.prop = Property.objects.create(
            owner=self.owner,
            title='API Test Property',
            description='Testing DRF API endpoint',
            property_type='APARTMENT',
            location='Tech Hub',
            rent=1800.00,
            bedrooms=2,
            bathrooms=1,
            is_available=True
        )

    def test_property_api_list(self):
        response = self.client.get(reverse('api_properties-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'API Test Property')

    def test_property_api_detail(self):
        response = self.client.get(reverse('api_properties-detail', kwargs={'pk': self.prop.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'API Test Property')

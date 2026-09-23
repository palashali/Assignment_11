from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from properties.models import Property, Favorite

User = get_user_model()


class PropertiesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner1 = User.objects.create_user(
            username='owner_one',
            email='owner1@test.com',
            password='password123',
            role='OWNER'
        )
        self.owner2 = User.objects.create_user(
            username='owner_two',
            email='owner2@test.com',
            password='password123',
            role='OWNER'
        )
        self.tenant = User.objects.create_user(
            username='tenant_user',
            email='tenant@test.com',
            password='password123',
            role='TENANT'
        )

        self.prop1 = Property.objects.create(
            owner=self.owner1,
            title='Downtown Loft',
            description='Modern loft in downtown',
            property_type='APARTMENT',
            location='Downtown City',
            rent=1500.00,
            bedrooms=2,
            bathrooms=1,
            is_available=True
        )

    def test_owner_can_create_property(self):
        self.client.login(username='owner_one', password='password123')
        response = self.client.post(reverse('properties:property_create'), {
            'title': 'Suburban Villa',
            'description': 'Spacious house with yard',
            'property_type': 'HOUSE',
            'location': 'Suburbs',
            'rent': '2500.00',
            'bedrooms': 3,
            'bathrooms': 2,
            'is_available': True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Property.objects.filter(title='Suburban Villa').exists())
        created_prop = Property.objects.get(title='Suburban Villa')
        self.assertEqual(created_prop.owner, self.owner1)

    def test_tenant_cannot_create_property(self):
        self.client.login(username='tenant_user', password='password123')
        response = self.client.post(reverse('properties:property_create'), {
            'title': 'Unauthorized Property',
            'description': 'Should fail',
            'property_type': 'APARTMENT',
            'location': 'Nowhere',
            'rent': '1000.00',
            'bedrooms': 1,
            'bathrooms': 1,
            'is_available': True,
        })
        # Should redirect with error
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Property.objects.filter(title='Unauthorized Property').exists())

    def test_owner_can_edit_own_property(self):
        self.client.login(username='owner_one', password='password123')
        response = self.client.post(reverse('properties:property_update', kwargs={'pk': self.prop1.pk}), {
            'title': 'Downtown Luxury Loft Updated',
            'description': 'Updated modern loft',
            'property_type': 'APARTMENT',
            'location': 'Downtown City',
            'rent': '1700.00',
            'bedrooms': 2,
            'bathrooms': 1,
            'is_available': True,
        })
        self.assertEqual(response.status_code, 302)
        self.prop1.refresh_from_db()
        self.assertEqual(self.prop1.title, 'Downtown Luxury Loft Updated')
        self.assertEqual(self.prop1.rent, 1700.00)

    def test_owner_cannot_edit_another_owners_property(self):
        self.client.login(username='owner_two', password='password123')
        response = self.client.post(reverse('properties:property_update', kwargs={'pk': self.prop1.pk}), {
            'title': 'Hacked Title',
            'description': 'Should not change',
            'property_type': 'APARTMENT',
            'location': 'Downtown City',
            'rent': '100.00',
            'bedrooms': 2,
            'bathrooms': 1,
            'is_available': True,
        })
        # Expect 403 Forbidden
        self.assertEqual(response.status_code, 403)
        self.prop1.refresh_from_db()
        self.assertEqual(self.prop1.title, 'Downtown Loft')

    def test_search_and_filter_properties(self):
        Property.objects.create(
            owner=self.owner1,
            title='Cozy Room near Metro',
            description='Affordable room',
            property_type='ROOM',
            location='Metro Station',
            rent=600.00,
            bedrooms=1,
            bathrooms=1,
            is_available=True
        )

        # Search by keyword
        resp1 = self.client.get(reverse('properties:property_list'), {'q': 'Metro'})
        self.assertEqual(len(resp1.context['page_obj']), 1)

        # Filter by property type
        resp2 = self.client.get(reverse('properties:property_list'), {'property_type': 'APARTMENT'})
        self.assertEqual(len(resp2.context['page_obj']), 1)

        # Filter by max rent
        resp3 = self.client.get(reverse('properties:property_list'), {'max_rent': '1000'})
        self.assertEqual(len(resp3.context['page_obj']), 1)

    def test_toggle_favorite(self):
        self.client.login(username='tenant_user', password='password123')
        response = self.client.get(reverse('properties:toggle_favorite', kwargs={'pk': self.prop1.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Favorite.objects.filter(user=self.tenant, property=self.prop1).exists())

        # Toggle again to remove
        self.client.get(reverse('properties:toggle_favorite', kwargs={'pk': self.prop1.pk}), follow=True)
        self.assertFalse(Favorite.objects.filter(user=self.tenant, property=self.prop1).exists())

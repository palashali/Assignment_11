from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from properties.models import Property
from rentals.models import RentalRequest

User = get_user_model()


class RentalsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username='prop_owner',
            email='owner@test.com',
            password='password123',
            role='OWNER'
        )
        self.tenant = User.objects.create_user(
            username='prop_tenant',
            email='tenant@test.com',
            password='password123',
            role='TENANT'
        )
        self.other_tenant = User.objects.create_user(
            username='other_tenant',
            email='other@test.com',
            password='password123',
            role='TENANT'
        )

        self.prop = Property.objects.create(
            owner=self.owner,
            title='Beachfront Cottage',
            description='Lovely cottage',
            property_type='HOUSE',
            location='Coastal Area',
            rent=2200.00,
            bedrooms=3,
            bathrooms=2,
            is_available=True
        )

    def test_tenant_send_rental_request(self):
        self.client.login(username='prop_tenant', password='password123')
        response = self.client.post(reverse('rentals:send_request', kwargs={'property_id': self.prop.pk}), {
            'message': 'I would love to rent this lovely beachfront cottage.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(RentalRequest.objects.filter(property=self.prop, tenant=self.tenant).exists())
        req = RentalRequest.objects.get(property=self.prop, tenant=self.tenant)
        self.assertEqual(req.status, RentalRequest.STATUS_PENDING)

    def test_owner_cannot_send_rental_request_own_property(self):
        self.client.login(username='prop_owner', password='password123')
        # Attempt request as owner
        response = self.client.post(reverse('rentals:send_request', kwargs={'property_id': self.prop.pk}), {
            'message': 'Requesting my own property'
        })
        # Role decorator or view logic redirects
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RentalRequest.objects.filter(property=self.prop, tenant=self.owner).exists())

    def test_cannot_send_duplicate_pending_request(self):
        RentalRequest.objects.create(
            property=self.prop,
            tenant=self.tenant,
            message='First request',
            status=RentalRequest.STATUS_PENDING
        )

        self.client.login(username='prop_tenant', password='password123')
        response = self.client.post(reverse('rentals:send_request', kwargs={'property_id': self.prop.pk}), {
            'message': 'Second duplicate request'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RentalRequest.objects.filter(property=self.prop, tenant=self.tenant).count(), 1)

    def test_tenant_can_cancel_pending_request(self):
        req = RentalRequest.objects.create(
            property=self.prop,
            tenant=self.tenant,
            message='Please accept',
            status=RentalRequest.STATUS_PENDING
        )

        self.client.login(username='prop_tenant', password='password123')
        response = self.client.post(reverse('rentals:cancel_request', kwargs={'pk': req.pk}))
        self.assertEqual(response.status_code, 302)
        req.refresh_from_db()
        self.assertEqual(req.status, RentalRequest.STATUS_CANCELLED)

    def test_owner_can_accept_and_reject_request(self):
        req = RentalRequest.objects.create(
            property=self.prop,
            tenant=self.tenant,
            message='Application note',
            status=RentalRequest.STATUS_PENDING
        )

        self.client.login(username='prop_owner', password='password123')
        accept_resp = self.client.post(reverse('rentals:accept_request', kwargs={'pk': req.pk}))
        self.assertEqual(accept_resp.status_code, 302)
        req.refresh_from_db()
        self.assertEqual(req.status, RentalRequest.STATUS_ACCEPTED)

        reject_resp = self.client.post(reverse('rentals:reject_request', kwargs={'pk': req.pk}))
        self.assertEqual(reject_resp.status_code, 302)
        req.refresh_from_db()
        self.assertEqual(req.status, RentalRequest.STATUS_REJECTED)

    def test_dashboards_render_properly(self):
        # Owner Dashboard
        self.client.login(username='prop_owner', password='password123')
        owner_resp = self.client.get(reverse('rentals:owner_dashboard'))
        self.assertEqual(owner_resp.status_code, 200)
        self.assertContains(owner_resp, 'Beachfront Cottage')

        # Tenant Dashboard
        self.client.login(username='prop_tenant', password='password123')
        tenant_resp = self.client.get(reverse('rentals:tenant_dashboard'))
        self.assertEqual(tenant_resp.status_code, 200)

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username='test_owner',
            email='owner@test.com',
            password='password123',
            role='OWNER',
            phone_number='1234567890'
        )
        self.tenant = User.objects.create_user(
            username='test_tenant',
            email='tenant@test.com',
            password='password123',
            role='TENANT'
        )

    def test_user_roles(self):
        self.assertTrue(self.owner.is_owner)
        self.assertFalse(self.owner.is_tenant)
        self.assertTrue(self.tenant.is_tenant)
        self.assertFalse(self.tenant.is_owner)

    def test_user_registration_owner(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'new_owner',
            'email': 'newowner@test.com',
            'first_name': 'New',
            'last_name': 'Owner',
            'role': 'OWNER',
            'password': 'password123',
            'confirm_password': 'password123',
            'phone_number': '9876543210',
            'bio': 'New owner bio'
        })
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(username='new_owner')
        self.assertEqual(new_user.role, 'OWNER')
        self.assertTrue(new_user.is_owner)

    def test_user_registration_password_mismatch(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'mismatch_user',
            'email': 'mismatch@test.com',
            'role': 'TENANT',
            'password': 'password123',
            'confirm_password': 'different_password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='mismatch_user').exists())

    def test_user_login_and_logout(self):
        login_response = self.client.post(reverse('accounts:login'), {
            'username': 'test_tenant',
            'password': 'password123'
        })
        self.assertEqual(login_response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

        logout_response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(logout_response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_profile_update(self):
        self.client.login(username='test_tenant', password='password123')
        response = self.client.post(reverse('accounts:profile'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com',
            'phone_number': '1112223333',
            'bio': 'Updated bio'
        })
        self.assertEqual(response.status_code, 302)
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.first_name, 'Updated')
        self.assertEqual(self.tenant.email, 'updated@test.com')

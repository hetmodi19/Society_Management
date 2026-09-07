from django.test import TestCase
from django.urls import reverse
from .models import User, ResidentProfile, LoginHistory

class AccountsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_resident',
            email='resident@example.com',
            password='Password123!',
            role=User.Role.RESIDENT,
            first_name='Test',
            last_name='Resident'
        )

    def test_user_properties(self):
        self.assertEqual(self.user.full_name, 'Test Resident')
        self.assertEqual(self.user.initials, 'TR')
        self.assertTrue(self.user.is_resident_user)
        self.assertFalse(self.user.is_society_admin)

    def test_login_flow(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'test_resident',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        # Verify login history was created
        log = LoginHistory.objects.filter(user=self.user).first()
        self.assertIsNotNone(log)
        self.assertTrue(log.is_successful)

    def test_login_flow_accepts_email(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'resident@example.com',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.wsgi_request.user, self.user)

    def test_demo_switcher(self):
        response = self.client.get(reverse('accounts:demo_switch', kwargs={'role': 'RESIDENT'}))
        self.assertEqual(response.status_code, 302)

    def test_security_settings_view(self):
        self.client.login(username='test_resident', password='Password123!')
        response = self.client.get(reverse('accounts:security'))
        self.assertEqual(response.status_code, 200)

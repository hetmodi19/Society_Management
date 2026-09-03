from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.properties.models import Wing, Unit
from apps.gatekeeper.models import PreApprovedPass, VisitorLog

class GatekeeperTests(TestCase):
    def setUp(self):
        self.guard = User.objects.create_user(
            username='guard_test',
            password='Password123!',
            role=User.Role.GUARD
        )
        self.resident = User.objects.create_user(
            username='resident_test',
            password='Password123!',
            role=User.Role.RESIDENT
        )
        self.wing = Wing.objects.create(name='Wing B', code='B')
        self.unit = Unit.objects.create(wing=self.wing, unit_number='B-101', primary_resident=self.resident)

    def test_passcode_verification(self):
        guest_pass = PreApprovedPass.objects.create(
            pass_code='998877',
            visitor_name='Special Guest',
            unit=self.unit,
            host_resident=self.resident,
            valid_until=timezone.now() + timedelta(hours=5)
        )

        self.client.login(username='guard_test', password='Password123!')
        response = self.client.post('/gatekeeper/verify-pass/', {
            'passcode': '998877'
        })
        self.assertEqual(response.status_code, 302)

        guest_pass.refresh_from_db()
        self.assertTrue(guest_pass.is_used)
        
        # Verify visitor log was automatically created
        visitor = VisitorLog.objects.filter(unit=self.unit, visitor_name='Special Guest').first()
        self.assertIsNotNone(visitor)
        self.assertEqual(visitor.status, VisitorLog.Status.INSIDE)

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.properties.models import Wing, Unit, MoveInOutRequest, RuleViolationReport

class PropertiesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='prop_user', password='Password123!', role=User.Role.RESIDENT)
        self.wing = Wing.objects.create(name='Wing Alpha', code='A')
        self.unit = Unit.objects.create(wing=self.wing, unit_number='A-101', primary_resident=self.user)

    def test_move_in_request(self):
        self.client.login(username='prop_user', password='Password123!')
        response = self.client.post('/properties/move-requests/', {
            'unit': self.unit.id,
            'move_type': 'MOVE_IN',
            'move_date': str(timezone.now().date() + timedelta(days=3)),
            'time_slot': 'Morning (08:00 AM - 12:00 PM)',
            'service_lift_required': True,
            'vehicle_count': 1,
            'moving_company_name': 'Best Movers',
        })
        self.assertEqual(response.status_code, 302)
        req = MoveInOutRequest.objects.filter(unit=self.unit).first()
        self.assertIsNotNone(req)
        self.assertEqual(req.status, MoveInOutRequest.Status.PENDING)

    def test_rule_violation_report(self):
        self.client.login(username='prop_user', password='Password123!')
        response = self.client.post('/properties/violations/', {
            'unit': self.unit.id,
            'violation_type': 'PARKING',
            'description': 'Blocking driveway space with van.',
        })
        self.assertEqual(response.status_code, 302)
        v = RuleViolationReport.objects.filter(unit=self.unit).first()
        self.assertIsNotNone(v)
        self.assertEqual(v.status, RuleViolationReport.Status.REPORTED)

from django.test import TestCase
from apps.accounts.models import User
from apps.properties.models import Wing, Unit
from apps.helpdesk.models import MaintenanceTicket

class HelpdeskTests(TestCase):
    def setUp(self):
        self.resident = User.objects.create_user(
            username='res_tck',
            password='Password123!',
            role=User.Role.RESIDENT
        )
        self.wing = Wing.objects.create(name='Wing C', code='C')
        self.unit = Unit.objects.create(wing=self.wing, unit_number='C-301', primary_resident=self.resident)

    def test_create_and_rate_ticket(self):
        ticket = MaintenanceTicket.objects.create(
            title='Corridor Light Blown',
            category=MaintenanceTicket.Category.ELECTRICAL,
            priority=MaintenanceTicket.Priority.HIGH,
            resident=self.resident,
            unit=self.unit,
            description='Bulb is flickering on 3rd floor.'
        )
        self.assertTrue(ticket.ticket_number.startswith('TCK-'))
        self.assertEqual(ticket.status, MaintenanceTicket.Status.OPEN)

        # Mark resolved and rate
        ticket.status = MaintenanceTicket.Status.RESOLVED
        ticket.rating = 5
        ticket.resident_feedback = 'Fixed rapidly!'
        ticket.save()

        self.assertEqual(ticket.rating, 5)

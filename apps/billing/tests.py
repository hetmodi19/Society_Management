from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from apps.accounts.models import User
from apps.properties.models import Wing, Unit
from apps.billing.models import MaintenanceBill, BillPayment

class BillingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='billing_user',
            password='Password123!',
            role=User.Role.RESIDENT,
            first_name='Billing',
            last_name='Tester'
        )
        self.wing = Wing.objects.create(name='Wing A', code='A')
        self.unit = Unit.objects.create(
            wing=self.wing,
            unit_number='A-101',
            floor=1,
            square_feet=1000,
            primary_resident=self.user
        )
        self.bill = MaintenanceBill.objects.create(
            bill_number='INV-TEST-001',
            unit=self.unit,
            resident=self.user,
            billing_month=date(2026, 9, 1),
            due_date=date(2026, 9, 15),
            total_amount=Decimal('4500.00'),
            status=MaintenanceBill.Status.UNPAID
        )

    def test_bill_payment_flow(self):
        self.assertEqual(self.bill.remaining_due, Decimal('4500.00'))
        
        self.client.login(username='billing_user', password='Password123!')
        response = self.client.post(f'/billing/bills/{self.bill.pk}/pay/', {
            'amount': 4500.00,
            'payment_method': 'UPI',
            'gateway_ref': 'UPI-TEST-123'
        })
        self.assertEqual(response.status_code, 302)

        self.bill.refresh_from_db()
        self.assertEqual(self.bill.status, MaintenanceBill.Status.PAID)
        self.assertEqual(self.bill.paid_amount, Decimal('4500.00'))

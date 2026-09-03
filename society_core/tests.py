from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User, ResidentProfile
from apps.properties.models import Wing, Unit
from apps.billing.models import MaintenanceBill, MaintenanceConfig
from apps.gatekeeper.models import PreApprovedPass, VisitorLog
from apps.helpdesk.models import MaintenanceTicket
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone

class SecurityAndRoleAccessTests(TestCase):
    def setUp(self):
        # Admin
        self.admin = User.objects.create_user(
            username='admin_sec',
            email='admin@sec.com',
            password='Password123!',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True
        )
        # Committee
        self.committee = User.objects.create_user(
            username='comm_sec',
            password='Password123!',
            role=User.Role.COMMITTEE
        )
        # Flat Owner A-101
        self.owner_a = User.objects.create_user(
            username='owner_a',
            password='Password123!',
            role=User.Role.RESIDENT,
            first_name='Owner',
            last_name='A'
        )
        # Tenant B-101
        self.tenant_b = User.objects.create_user(
            username='tenant_b',
            password='Password123!',
            role=User.Role.RESIDENT,
            first_name='Tenant',
            last_name='B'
        )
        # Guard
        self.guard = User.objects.create_user(
            username='guard_sec',
            password='Password123!',
            role=User.Role.GUARD
        )
        # Staff
        self.staff = User.objects.create_user(
            username='staff_sec',
            password='Password123!',
            role=User.Role.STAFF
        )

        self.wing = Wing.objects.create(name='Wing Alpha', code='WA')

        # Unit A (Owner occupied)
        self.unit_a = Unit.objects.create(
            wing=self.wing,
            unit_number='WA-101',
            occupancy_status=Unit.OccupancyStatus.OWNER,
            owner=self.owner_a,
            primary_resident=self.owner_a,
            square_feet=1200
        )

        # Unit B (Rented: Owned by committee, Rented by tenant_b)
        self.unit_b = Unit.objects.create(
            wing=self.wing,
            unit_number='WA-102',
            occupancy_status=Unit.OccupancyStatus.TENANT,
            owner=self.committee,
            primary_resident=self.tenant_b,
            square_feet=1000
        )

        # Bill for Unit A
        self.bill_a = MaintenanceBill.objects.create(
            bill_number='INV-TEST-A101',
            unit=self.unit_a,
            resident=self.owner_a,
            billing_month=date(2026, 9, 1),
            due_date=date(2026, 9, 15),
            total_amount=Decimal('4200.00'),
            status=MaintenanceBill.Status.UNPAID
        )

        # Bill for Unit B
        self.bill_b = MaintenanceBill.objects.create(
            bill_number='INV-TEST-B102',
            unit=self.unit_b,
            resident=self.tenant_b,
            billing_month=date(2026, 9, 1),
            due_date=date(2026, 9, 15),
            total_amount=Decimal('3500.00'),
            status=MaintenanceBill.Status.UNPAID
        )

        # Pass for Unit A
        self.pass_a = PreApprovedPass.objects.create(
            pass_code='112233',
            visitor_name='Guest of A',
            unit=self.unit_a,
            host_resident=self.owner_a,
            valid_until=timezone.now() + timedelta(hours=12)
        )

    # 1. Unauthenticated Redirection Tests
    def test_unauthenticated_access_redirects_to_login(self):
        protected_urls = [
            '/dashboard/',
            '/billing/bills/',
            '/billing/ledger/',
            '/gatekeeper/terminal/',
            '/gatekeeper/passes/',
            '/helpdesk/tickets/',
            '/amenities/',
            '/properties/units/',
            '/communications/notices/',
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, f"URL {url} did not redirect unauthenticated user.")
            self.assertIn('/accounts/login/', response.url)

    # 2. RBAC Permission Checks
    def test_resident_cannot_access_guard_terminal(self):
        self.client.login(username='owner_a', password='Password123!')
        response = self.client.get(reverse('gatekeeper:terminal'))
        # Should be redirected to dashboard with permission denied
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_resident_cannot_access_financial_ledger(self):
        self.client.login(username='tenant_b', password='Password123!')
        response = self.client.get(reverse('billing:ledger'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_resident_cannot_access_batch_bill_generation(self):
        self.client.login(username='owner_a', password='Password123!')
        response = self.client.get(reverse('billing:generate_bills'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_guard_accesses_terminal_successfully(self):
        self.client.login(username='guard_sec', password='Password123!')
        response = self.client.get(reverse('gatekeeper:terminal'))
        self.assertEqual(response.status_code, 200)

    def test_committee_accesses_ledger_successfully(self):
        self.client.login(username='comm_sec', password='Password123!')
        response = self.client.get(reverse('billing:ledger'))
        self.assertEqual(response.status_code, 200)

    # 3. Owner vs Tenant Flat Data Isolation
    def test_owner_can_view_own_flat_detail(self):
        self.client.login(username='owner_a', password='Password123!')
        response = self.client.get(reverse('properties:unit_detail', kwargs={'pk': self.unit_a.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'WA-101')

    def test_owner_cannot_view_other_flat_detail(self):
        self.client.login(username='owner_a', password='Password123!')
        response = self.client.get(reverse('properties:unit_detail', kwargs={'pk': self.unit_b.pk}))
        # Blocked and redirected to units list
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('properties:units'))

    def test_tenant_can_view_own_rented_flat_detail(self):
        self.client.login(username='tenant_b', password='Password123!')
        response = self.client.get(reverse('properties:unit_detail', kwargs={'pk': self.unit_b.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'WA-102')

    def test_tenant_cannot_view_other_flat_detail(self):
        self.client.login(username='tenant_b', password='Password123!')
        response = self.client.get(reverse('properties:unit_detail', kwargs={'pk': self.unit_a.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('properties:units'))

    def test_cross_flat_bill_privacy(self):
        # Tenant B tries to view Bill A
        self.client.login(username='tenant_b', password='Password123!')
        response = self.client.get(reverse('billing:detail', kwargs={'pk': self.bill_a.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('billing:bills'))

    # 4. Role Dashboards
    def test_admin_dashboard_rendering(self):
        self.client.login(username='admin_sec', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Society Executive Overview')

    def test_resident_dashboard_rendering(self):
        self.client.login(username='owner_a', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Home')

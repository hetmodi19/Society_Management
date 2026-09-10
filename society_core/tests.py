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

    # 1. Unauthenticated Redirection & Universal Multi-Identifier Login Tests
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

    def test_login_via_exact_username(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'admin_sec',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_login_via_case_insensitive_username(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'ADMIN_SEC',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_login_via_email(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'admin@sec.com',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_login_via_flat_number(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'WA-101',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_login_via_full_name(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'Owner A',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

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

    # 4. Role Dashboards & Data Synchronization Tests
    def test_admin_dashboard_rendering(self):
        self.client.login(username='admin_sec', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Society Executive Overview')
        # Check that context variables exist and are mathematically sound
        self.assertEqual(response.context['total_units'], 2)
        self.assertEqual(response.context['occupied_units'], 2)
        self.assertEqual(response.context['owner_occupied_units'], 1)
        self.assertEqual(response.context['rented_units'], 1)
        self.assertEqual(response.context['vacant_units'], 0)
        self.assertEqual(response.context['occupancy_rate'], 100.0)

    def test_admin_dashboard_metrics_data_driven(self):
        from apps.billing.models import BillPayment, SocietyExpense
        from apps.amenities.models import Amenity, AmenityBooking, EVChargingStation, EVChargingSession
        from datetime import time

        today = timezone.now().date()
        cur_year = today.year
        cur_month = today.month

        # Record a maintenance payment for Bill A (2000 paid)
        BillPayment.objects.create(
            bill=self.bill_a,
            transaction_id='TXN-TEST-DASH-1',
            receipt_number='RCPT-TEST-DASH-1',
            payer=self.owner_a,
            amount=Decimal('2000.00'),
            payment_status=BillPayment.PaymentStatus.SUCCESS,
            payment_date=timezone.now()
        )
        self.bill_a.paid_amount = Decimal('2000.00')
        self.bill_a.update_status()
        self.bill_a.save()

        # Add Amenity Booking with fee
        amenity = Amenity.objects.create(name='Banquet Hall', slug='banquet-dash', hourly_rate=Decimal('500.00'))
        AmenityBooking.objects.create(
            amenity=amenity,
            resident=self.owner_a,
            unit=self.unit_a,
            booking_date=today,
            start_time=time(10, 0),
            end_time=time(14, 0),
            total_fee=Decimal('2000.00'),
            status=AmenityBooking.Status.CONFIRMED
        )

        # Add EV Charging Session
        ev_st = EVChargingStation.objects.create(station_name='EV-Bay-1')
        EVChargingSession.objects.create(
            station=ev_st,
            user=self.owner_a,
            unit=self.unit_a,
            booking_date=today,
            start_time=time(15, 0),
            end_time=time(17, 0),
            total_cost=Decimal('500.00'),
            status=EVChargingSession.SessionStatus.COMPLETED
        )

        # Add Approved Expense
        SocietyExpense.objects.create(
            title='Water Tanker',
            amount=Decimal('1500.00'),
            expense_date=today,
            is_approved=True
        )

        # Add Helpdesk Ticket
        MaintenanceTicket.objects.create(
            resident=self.owner_a,
            unit=self.unit_a,
            title='Leaky tap',
            status=MaintenanceTicket.Status.OPEN
        )

        self.client.login(username='admin_sec', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        # Expected Monthly Revenue = 2000 (Maint) + 2000 (Amenity) + 500 (EV) = 4500.00
        self.assertEqual(response.context['total_revenue'], Decimal('4500.00'))
        self.assertEqual(response.context['total_monthly_collections'], Decimal('4500.00'))

        # Expected Outstanding Dues = (4200 - 2000 = 2200) + 3500 = 5700.00
        self.assertEqual(response.context['outstanding_dues'], Decimal('5700.00'))

        # Expected Pending Tickets = 1
        self.assertEqual(response.context['pending_tickets'], 1)

        # Cashflow series length must be 6
        self.assertEqual(len(response.context['cashflow_labels']), 6)
        self.assertEqual(len(response.context['cashflow_revenue']), 6)
        self.assertEqual(len(response.context['cashflow_expenses']), 6)
        # Current month (last element) must match
        self.assertEqual(response.context['cashflow_revenue'][-1], 4500.00)
        self.assertEqual(response.context['cashflow_expenses'][-1], 1500.00)

    def test_resident_dashboard_rendering(self):
        self.client.login(username='owner_a', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Home')
        self.assertEqual(response.context['total_unpaid_amount'], Decimal('4200.00'))

    def test_secretary_dashboard_rendering(self):
        secretary = User.objects.create_user(
            username='sec_user',
            password='Password123!',
            role=User.Role.SECRETARY,
            first_name='Ananya',
            last_name='Deshmukh'
        )
        self.client.login(username='sec_user', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/secretary_dashboard.html')
        self.assertContains(response, 'Hon. Secretary Portal')
        self.assertContains(response, 'Society Administration Desk')

    def test_treasurer_dashboard_rendering(self):
        treasurer = User.objects.create_user(
            username='treas_user',
            password='Password123!',
            role=User.Role.TREASURER,
            first_name='Kavita',
            last_name='Iyer'
        )
        self.client.login(username='treas_user', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/treasurer_dashboard.html')
        self.assertContains(response, 'Treasurer & Accounts')
        self.assertContains(response, 'Society Treasury & Financial Ledger')

    def test_facility_manager_dashboard_rendering(self):
        facility_mgr = User.objects.create_user(
            username='fac_user',
            password='Password123!',
            role=User.Role.FACILITY_MGR,
            first_name='Ramesh',
            last_name='Joshi'
        )
        self.client.login(username='fac_user', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/facility_dashboard.html')
        self.assertContains(response, 'Facility Manager Portal')
        self.assertContains(response, 'Facility & Infrastructure Operations')

    def test_tenant_dashboard_rendering(self):
        tenant_user = User.objects.create_user(
            username='priya_tenant',
            password='Password123!',
            role=User.Role.TENANT,
            first_name='Priya',
            last_name='Patel'
        )
        self.unit_b.primary_resident = tenant_user
        self.unit_b.save()
        self.client.login(username='priya_tenant', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/tenant_dashboard.html')
        self.assertContains(response, 'Tenant Resident')
        self.assertContains(response, 'Flat WA-102')

    def test_guard_redirects_to_gate_terminal(self):
        self.client.login(username='guard_sec', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('gatekeeper:terminal'))

    def test_demo_switcher_all_personas(self):
        self.client.login(username='admin_sec', password='Password123!')
        # Test switching to admin
        res = self.client.get(reverse('accounts:demo_switch', kwargs={'role': 'ADMIN'}), follow=True)
        self.assertEqual(res.status_code, 200)
        # Test switching to guard
        res = self.client.get(reverse('accounts:demo_switch', kwargs={'role': 'GUARD'}), follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.client.session['_auth_user_id'], str(self.guard.pk))



from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User, ResidentProfile
from apps.properties.models import Wing, Unit, MoveInOutRequest, RuleViolationReport

class PropertiesTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_test',
            password='Password123!',
            role=User.Role.ADMIN,
            first_name='Rajesh',
            last_name='Sharma',
            is_staff=True,
            is_superuser=True
        )
        self.owner_user = User.objects.create_user(
            username='owner_test',
            password='Password123!',
            role=User.Role.RESIDENT,
            first_name='Vikram',
            last_name='Malhotra'
        )
        self.tenant_user = User.objects.create_user(
            username='tenant_test',
            password='Password123!',
            role=User.Role.RESIDENT,
            first_name='Priya',
            last_name='Patel'
        )
        self.wing = Wing.objects.create(name='Wing Alpha', code='A')

        # 1. Owner Occupied
        self.unit_owner = Unit.objects.create(
            wing=self.wing,
            unit_number='A-101',
            occupancy_status=Unit.OccupancyStatus.OWNER,
            owner=self.owner_user,
            primary_resident=self.owner_user,
            square_feet=1500
        )

        # 2. Tenant Occupied (Rented)
        self.unit_tenant = Unit.objects.create(
            wing=self.wing,
            unit_number='A-102',
            occupancy_status=Unit.OccupancyStatus.TENANT,
            owner=self.admin,
            primary_resident=self.tenant_user,
            square_feet=1200
        )

        # 3. Vacant Flat
        self.unit_vacant = Unit.objects.create(
            wing=self.wing,
            unit_number='A-103',
            occupancy_status=Unit.OccupancyStatus.VACANT,
            square_feet=1100
        )

    def test_move_in_request(self):
        self.client.login(username='owner_test', password='Password123!')
        response = self.client.post('/properties/move-requests/', {
            'unit': self.unit_owner.id,
            'move_type': 'MOVE_IN',
            'move_date': str(timezone.now().date() + timedelta(days=3)),
            'time_slot': 'Morning (08:00 AM - 12:00 PM)',
            'service_lift_required': True,
            'vehicle_count': 1,
            'moving_company_name': 'Best Movers',
        })
        self.assertEqual(response.status_code, 302)
        req = MoveInOutRequest.objects.filter(unit=self.unit_owner).first()
        self.assertIsNotNone(req)
        self.assertEqual(req.status, MoveInOutRequest.Status.PENDING)

    def test_rule_violation_report(self):
        self.client.login(username='owner_test', password='Password123!')
        response = self.client.post('/properties/violations/', {
            'unit': self.unit_owner.id,
            'violation_type': 'PARKING',
            'description': 'Blocking driveway space with van.',
        })
        self.assertEqual(response.status_code, 302)
        v = RuleViolationReport.objects.filter(unit=self.unit_owner).first()
        self.assertIsNotNone(v)
        self.assertEqual(v.status, RuleViolationReport.Status.REPORTED)

    def test_unit_list_occupancy_rendering(self):
        self.client.login(username='admin_test', password='Password123!')
        response = self.client.get('/properties/units/')
        self.assertEqual(response.status_code, 200)

        # Flat A-101 (Occupied / Owner)
        self.assertContains(response, 'Flat A-101')
        self.assertContains(response, 'Occupied')
        self.assertContains(response, 'Vikram Malhotra')

        # Flat A-102 (Rented / Tenant)
        self.assertContains(response, 'Flat A-102')
        self.assertContains(response, 'Rented')
        self.assertContains(response, 'Rajesh Sharma')
        self.assertContains(response, 'Priya Patel')

        # Flat A-103 (Vacant)
        self.assertContains(response, 'Flat A-103')
        self.assertContains(response, 'Vacant')

    def test_admin_add_and_edit_unit(self):
        self.client.login(username='admin_test', password='Password123!')

        # Add Unit
        add_response = self.client.post('/properties/units/add/', {
            'wing': self.wing.id,
            'unit_number': 'A-505',
            'floor': 5,
            'unit_type': '3BHK',
            'square_feet': 1600,
            'occupancy_status': 'OWNER',
            'owner': self.owner_user.id,
            'primary_resident': self.owner_user.id,
            'parking_slot_number': 'P-A505',
            'intercom_extension': '505',
        })
        self.assertEqual(add_response.status_code, 302)
        created_unit = Unit.objects.filter(unit_number='A-505').first()
        self.assertIsNotNone(created_unit)
        self.assertEqual(created_unit.occupancy_status, Unit.OccupancyStatus.OWNER)

        # Edit Unit to VACANT
        edit_response = self.client.post(f'/properties/units/{created_unit.id}/edit/', {
            'wing': self.wing.id,
            'unit_number': 'A-505',
            'floor': 5,
            'unit_type': '3BHK',
            'square_feet': 1600,
            'occupancy_status': 'VACANT',
            'parking_slot_number': 'P-A505',
            'intercom_extension': '505',
        })
        self.assertEqual(edit_response.status_code, 302)
        created_unit.refresh_from_db()
        self.assertEqual(created_unit.occupancy_status, Unit.OccupancyStatus.VACANT)

    def test_admin_add_and_edit_resident(self):
        self.client.login(username='admin_test', password='Password123!')

        # Register Resident
        add_response = self.client.post('/properties/residents/add/', {
            'first_name': 'Sneha',
            'last_name': 'Joshi',
            'username': 'sneha_j_test',
            'email': 'sneha.joshi@example.com',
            'phone_number': '+91 98200 44332',
            'password': 'resident123',
            'resident_type': 'OWNER',
            'unit': self.unit_vacant.id,
            'occupation': 'Cardiologist',
        })
        self.assertEqual(add_response.status_code, 302)
        new_res = User.objects.filter(username='sneha_j_test').first()
        self.assertIsNotNone(new_res)
        self.assertEqual(new_res.full_name, 'Sneha Joshi')
        self.unit_vacant.refresh_from_db()
        self.assertEqual(self.unit_vacant.occupancy_status, Unit.OccupancyStatus.OWNER)
        self.assertEqual(self.unit_vacant.owner, new_res)

    def test_admin_delete_unit(self):
        self.client.login(username='admin_test', password='Password123!')
        del_response = self.client.post(f'/properties/units/{self.unit_vacant.id}/delete/')
        self.assertEqual(del_response.status_code, 302)
        self.assertFalse(Unit.objects.filter(id=self.unit_vacant.id).exists())

    def test_admin_delete_resident(self):
        self.client.login(username='admin_test', password='Password123!')
        del_response = self.client.post(f'/properties/residents/{self.tenant_user.id}/delete/')
        self.assertEqual(del_response.status_code, 302)
        self.assertFalse(User.objects.filter(id=self.tenant_user.id).exists())


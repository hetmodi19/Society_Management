from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta, time
from decimal import Decimal
import random

from apps.accounts.models import User, ResidentProfile, StaffProfile, LoginHistory
from apps.properties.models import Wing, Unit, ResidentUnitMapping, Vehicle, DomesticStaff, MoveInOutRequest, RuleViolationReport
from apps.billing.models import MaintenanceConfig, MaintenanceBill, BillPayment, SocietyExpense
from apps.gatekeeper.models import VisitorLog, PreApprovedPass, ParcelLog, SOSAlert
from apps.helpdesk.models import MaintenanceTicket, TicketComment
from apps.amenities.models import Amenity, AmenityBooking, EVChargingStation, EVChargingSession
from apps.communications.models import Notice, SocietyPoll, PollOption, PollVote, DiscussionPost, DiscussionReply, LostAndFoundItem, SocietyDocument

class Command(BaseCommand):
    help = 'Seeds realistic Indian demonstration data for SmartSociety 360'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting SmartSociety 360 Indian data seeding...'))

        # 1. Maintenance Config
        config, created = MaintenanceConfig.objects.get_or_create(
            id=1,
            defaults={
                'name': 'Emerald Greens CHS Ltd. Standard Billing Policy',
                'base_rate_per_sqft': Decimal('3.50'),
                'sinking_fund_rate': Decimal('0.50'),
                'parking_slot_fee': Decimal('300.00'),
                'water_fixed_charge': Decimal('400.00'),
                'fixed_amenities_fee': Decimal('500.00'),
                'late_fee_percentage': Decimal('2.00'),
                'payment_grace_days': 15,
                'is_active': True,

            }
        )
        if not created:
            config.name = 'Emerald Greens CHS Ltd. Standard Billing Policy'
            config.base_rate_per_sqft = Decimal('3.50')
            config.sinking_fund_rate = Decimal('0.50')
            config.parking_slot_fee = Decimal('300.00')
            config.water_fixed_charge = Decimal('400.00')
            config.fixed_amenities_fee = Decimal('500.00')
            config.late_fee_percentage = Decimal('2.00')
            config.payment_grace_days = 15
            config.save()

        # 2. Key Users across all 5 roles (Authentic Indian Personas)
        # Admin / President
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@emeraldgreens.residence',
                'first_name': 'Rajesh',

                'last_name': 'Sharma',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'phone_number': '+91 98201 12345',

                'two_factor_enabled': True,
                'security_pin': '8899',
            }
        )
        admin_user.first_name = 'Rajesh'
        admin_user.last_name = 'Sharma'
        admin_user.email = 'admin@emeraldgreens.residence'
        admin_user.phone_number = '+91 98201 12345'
        admin_user.role = User.Role.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password('admin123')
        admin_user.save()

        # Hon. Secretary
        secretary_user, _ = User.objects.get_or_create(
            username='secretary',
            defaults={
                'email': 'secretary@emeraldgreens.residence',
                'first_name': 'Ananya',
                'last_name': 'Deshmukh',
                'role': User.Role.SECRETARY,
                'phone_number': '+91 98202 23456',

                'security_pin': '4455',
            }
        )
        secretary_user.first_name = 'Ananya'
        secretary_user.last_name = 'Deshmukh'
        secretary_user.email = 'secretary@emeraldgreens.residence'
        secretary_user.phone_number = '+91 98202 23456'
        secretary_user.role = User.Role.SECRETARY
        secretary_user.set_password('committee123')
        secretary_user.save()

        # Hon. Treasurer
        treasurer_user, _ = User.objects.get_or_create(
            username='treasurer',
            defaults={
                'email': 'treasurer@emeraldgreens.residence',
                'first_name': 'Kavita',
                'last_name': 'Iyer',
                'role': User.Role.TREASURER,
                'phone_number': '+91 98207 78901',
                'security_pin': '7788',
            }
        )
        treasurer_user.first_name = 'Kavita'
        treasurer_user.last_name = 'Iyer'
        treasurer_user.email = 'treasurer@emeraldgreens.residence'
        treasurer_user.phone_number = '+91 98207 78901'
        treasurer_user.role = User.Role.TREASURER
        treasurer_user.set_password('treasurer123')
        treasurer_user.save()

        # Facility Manager
        facility_user, _ = User.objects.get_or_create(
            username='facility_mgr',
            defaults={
                'email': 'facility@emeraldgreens.residence',
                'first_name': 'Ramesh',
                'last_name': 'Joshi',
                'role': User.Role.FACILITY_MGR,
                'phone_number': '+91 98208 89012',
                'security_pin': '3344',
            }
        )
        facility_user.first_name = 'Ramesh'
        facility_user.last_name = 'Joshi'
        facility_user.email = 'facility@emeraldgreens.residence'
        facility_user.phone_number = '+91 98208 89012'
        facility_user.role = User.Role.FACILITY_MGR
        facility_user.set_password('facility123')
        facility_user.save()

        # Society Accountant
        accountant_user, _ = User.objects.get_or_create(
            username='accountant',
            defaults={
                'email': 'accountant@emeraldgreens.residence',
                'first_name': 'Deepak',
                'last_name': 'Parekh',
                'role': User.Role.ACCOUNTANT,
                'phone_number': '+91 98209 90123',
                'security_pin': '5566',
            }
        )
        accountant_user.first_name = 'Deepak'
        accountant_user.last_name = 'Parekh'
        accountant_user.email = 'accountant@emeraldgreens.residence'
        accountant_user.phone_number = '+91 98209 90123'
        accountant_user.role = User.Role.ACCOUNTANT
        accountant_user.set_password('accountant123')
        accountant_user.save()

        # Resident Owner (Vikram Malhotra - Flat A-402)
        resident_owner, _ = User.objects.get_or_create(
            username='john_doe',
            defaults={
                'email': 'vikram.malhotra@example.com',
                'first_name': 'Vikram',
                'last_name': 'Malhotra',
                'role': User.Role.OWNER,
                'phone_number': '+91 98203 34567',

                'security_pin': '1234',
            }
        )
        resident_owner.first_name = 'Vikram'
        resident_owner.last_name = 'Malhotra'
        resident_owner.email = 'vikram.malhotra@example.com'
        resident_owner.phone_number = '+91 98203 34567'
        resident_owner.role = User.Role.OWNER
        resident_owner.set_password('resident123')
        resident_owner.save()

        # Convenience alias for Owner login
        owner_alias, _ = User.objects.get_or_create(
            username='owner',
            defaults={
                'email': 'owner@emeraldgreens.residence',
                'first_name': 'Vikram',
                'last_name': 'Malhotra',
                'role': User.Role.OWNER,
                'phone_number': '+91 98203 34568',
                'security_pin': '1234',
            }
        )
        owner_alias.first_name = 'Vikram'
        owner_alias.last_name = 'Malhotra'
        owner_alias.role = User.Role.OWNER
        owner_alias.set_password('resident123')
        owner_alias.save()

        res_prof1, _ = ResidentProfile.objects.get_or_create(
            user=resident_owner,
            defaults={
                'resident_type': ResidentProfile.ResidentType.OWNER,
                'emergency_contact_name': 'Pooja Malhotra',
                'emergency_contact_phone': '+91 98203 99887',
                'blood_group': 'O+',
                'occupation': 'Principal Cloud Architect',

                'intercom_number': '1402',
            }
        )
        res_prof1.resident_type = ResidentProfile.ResidentType.OWNER
        res_prof1.emergency_contact_name = 'Pooja Malhotra'
        res_prof1.emergency_contact_phone = '+91 98203 99887'
        res_prof1.blood_group = 'O+'
        res_prof1.occupation = 'Principal Cloud Architect'
        res_prof1.intercom_number = '1402'
        res_prof1.save()

        # Resident Tenant (Priya Patel - Flat B-201)
        resident_tenant, _ = User.objects.get_or_create(
            username='sarah_smith',
            defaults={
                'email': 'priya.patel@example.com',
                'first_name': 'Priya',
                'last_name': 'Patel',
                'role': User.Role.TENANT,
                'phone_number': '+91 98204 45678',

                'security_pin': '5678',
            }
        )
        resident_tenant.first_name = 'Priya'
        resident_tenant.last_name = 'Patel'
        resident_tenant.email = 'priya.patel@example.com'
        resident_tenant.phone_number = '+91 98204 45678'
        resident_tenant.role = User.Role.TENANT
        resident_tenant.set_password('resident123')
        resident_tenant.save()

        # Convenience alias for Tenant login
        tenant_alias, _ = User.objects.get_or_create(
            username='tenant',
            defaults={
                'email': 'tenant@emeraldgreens.residence',
                'first_name': 'Priya',
                'last_name': 'Patel',
                'role': User.Role.TENANT,
                'phone_number': '+91 98204 45679',
                'security_pin': '5678',
            }
        )
        tenant_alias.first_name = 'Priya'
        tenant_alias.last_name = 'Patel'
        tenant_alias.role = User.Role.TENANT
        tenant_alias.set_password('resident123')
        tenant_alias.save()

        res_prof2, _ = ResidentProfile.objects.get_or_create(
            user=resident_tenant,
            defaults={
                'resident_type': ResidentProfile.ResidentType.TENANT,
                'emergency_contact_name': 'Suresh Patel',
                'emergency_contact_phone': '+91 98204 88776',
                'blood_group': 'A+',
                'occupation': 'Senior Product Specialist',

                'intercom_number': '1201',
            }
        )
        res_prof2.resident_type = ResidentProfile.ResidentType.TENANT
        res_prof2.emergency_contact_name = 'Suresh Patel'
        res_prof2.emergency_contact_phone = '+91 98204 88776'
        res_prof2.blood_group = 'A+'
        res_prof2.occupation = 'Senior Product Specialist'
        res_prof2.intercom_number = '1201'
        res_prof2.save()

        # Security Guard
        guard_user, _ = User.objects.get_or_create(
            username='guard_raj',
            defaults={
                'email': 'security.rajesh@emeraldgreens.residence',
                'first_name': 'Rajesh',
                'last_name': 'Gurjar',
                'role': User.Role.GUARD,
                'phone_number': '+91 98205 56789',

            }
        )
        guard_user.first_name = 'Rajesh'
        guard_user.last_name = 'Gurjar'
        guard_user.email = 'security.rajesh@emeraldgreens.residence'
        guard_user.phone_number = '+91 98205 56789'
        guard_user.role = User.Role.GUARD
        guard_user.set_password('guard123')
        guard_user.save()

        # Guard alias
        guard_alias, _ = User.objects.get_or_create(
            username='guard',
            defaults={
                'email': 'guard@emeraldgreens.residence',
                'first_name': 'Rajesh',
                'last_name': 'Gurjar',
                'role': User.Role.GUARD,
                'phone_number': '+91 98205 56780',
            }
        )
        guard_alias.first_name = 'Rajesh'
        guard_alias.last_name = 'Gurjar'
        guard_alias.role = User.Role.GUARD
        guard_alias.set_password('guard123')
        guard_alias.save()

        # Facility Technician
        staff_electrician, _ = User.objects.get_or_create(
            username='mike_electrician',
            defaults={
                'email': 'mukesh.tech@emeraldgreens.residence',
                'first_name': 'Mukesh',
                'last_name': 'Sharma',
                'role': User.Role.STAFF,
                'phone_number': '+91 98206 67890',

            }
        )
        staff_electrician.first_name = 'Mukesh'
        staff_electrician.last_name = 'Sharma'
        staff_electrician.email = 'mukesh.tech@emeraldgreens.residence'
        staff_electrician.phone_number = '+91 98206 67890'
        staff_electrician.role = User.Role.STAFF
        staff_electrician.set_password('staff123')
        staff_electrician.save()

        # Staff alias
        staff_alias, _ = User.objects.get_or_create(
            username='staff',
            defaults={
                'email': 'staff@emeraldgreens.residence',
                'first_name': 'Mukesh',
                'last_name': 'Sharma',
                'role': User.Role.STAFF,
                'phone_number': '+91 98206 67891',
            }
        )
        staff_alias.first_name = 'Mukesh'
        staff_alias.last_name = 'Sharma'
        staff_alias.role = User.Role.STAFF
        staff_alias.set_password('staff123')
        staff_alias.save()

        staff_prof, _ = StaffProfile.objects.get_or_create(
            user=staff_electrician,
            defaults={
                'specialization': StaffProfile.Specialization.ELECTRICIAN,
                'badge_number': 'TECH-E-04',
                'duty_shift': 'Day Shift (08:00 AM - 05:00 PM)',
                'is_on_duty': True,
                'rating': Decimal('4.9'),
            }
        )
        staff_prof.specialization = StaffProfile.Specialization.ELECTRICIAN
        staff_prof.badge_number = 'TECH-E-04'
        staff_prof.duty_shift = 'Day Shift (08:00 AM - 05:00 PM)'
        staff_prof.is_on_duty = True
        staff_prof.rating = Decimal('4.9')
        staff_prof.save()

        StaffProfile.objects.get_or_create(
            user=staff_alias,
            defaults={
                'specialization': StaffProfile.Specialization.ELECTRICIAN,
                'badge_number': 'TECH-E-05',
                'duty_shift': 'Day Shift (08:00 AM - 05:00 PM)',
                'is_on_duty': True,
                'rating': Decimal('4.9'),
            }
        )

        # Migrate records from older seed versions before creating renamed Indian records.
        User.objects.filter(username='admin').update(first_name='Amit', last_name='Sharma', email='admin@emeraldgreens.residence')
        User.objects.filter(username='secretary').update(first_name='Neha', last_name='Deshmukh', email='secretary@emeraldgreens.residence')
        User.objects.filter(username='john_doe').update(first_name='Vikram', last_name='Joshi', email='amit.sharma@example.in')
        User.objects.filter(username='sarah_smith').update(first_name='Pooja', last_name='Verma', email='pooja.verma@example.in')
        User.objects.filter(username='mike_electrician').update(first_name='Sanjay', last_name='Pawar', email='sanjay.pawar@emeraldgreens.residence')
        ResidentProfile.objects.filter(user=resident_owner).update(emergency_contact_name='Kavita Joshi', occupation='Software Engineer')
        ResidentProfile.objects.filter(user=resident_tenant).update(emergency_contact_name='Rakesh Verma', occupation='Chartered Accountant')
        Vehicle.objects.filter(license_plate='NY-8492-EG').update(license_plate='MH-02-EQ-8492', make_model='Tata Nexon EV (Glacier White)')
        Vehicle.objects.filter(license_plate='NY-3109-AB').update(license_plate='MH-01-AB-3109', make_model='Maruti Suzuki Grand Vitara (Pearl White)')
        DomesticStaff.objects.filter(name='Maria Santos').update(name='Sunita Jadhav')
        Amenity.objects.filter(slug='olympic-infinity-pool').update(name='Emerald Greens Swimming Pool', description="Temperature-controlled pool with a separate children's area for residents.")
        Amenity.objects.filter(slug='grand-banquet-hall').update(name='Sahyadri Community Hall', description='Air-conditioned community hall for birthdays, festivals and society meetings.')
        LostAndFoundItem.objects.filter(item_name='BMW Car Smart Key FOB with Blue Lanyard').update(item_name='Maruti Suzuki Car Key with Red Lanyard', contact_phone='+91 98765 43212')
        LostAndFoundItem.objects.filter(item_name='Apple AirPods Pro (2nd Gen) in White Case').update(item_name='Boat Wireless Earbuds in Black Case', contact_phone='+91 98765 43213')
        resident_owner.refresh_from_db()
        resident_tenant.refresh_from_db()

        # Login records
        LoginHistory.objects.get_or_create(
            user=resident_owner,
            ip_address='192.168.1.45',
            defaults={'device_type': 'Desktop Workstation (Chrome Windows)', 'user_agent': 'Mozilla/5.0 Windows NT 10.0', 'is_successful': True}
        )

        self.stdout.write(self.style.SUCCESS('  [OK] Created Indian users & security profiles.'))

        # 3. Wings & Flats
        wing_a, created_a = Wing.objects.get_or_create(code='A', defaults={'name': 'Wing A - Aravali Tower', 'total_floors': 12})
        if not created_a:
            wing_a.name = 'Wing A - Aravali Tower'
            wing_a.total_floors = 12
            wing_a.save()

        wing_b, created_b = Wing.objects.get_or_create(code='B', defaults={'name': 'Wing B - Nilgiri Crest', 'total_floors': 12})
        if not created_b:
            wing_b.name = 'Wing B - Nilgiri Crest'
            wing_b.total_floors = 12
            wing_b.save()

        wing_c, created_c = Wing.objects.get_or_create(code='C', defaults={'name': 'Wing C - Sahyadri Heights', 'total_floors': 15})
        if not created_c:
            wing_c.name = 'Wing C - Sahyadri Heights'
            wing_c.total_floors = 15
            wing_c.save()

        unit_a402, _ = Unit.objects.get_or_create(
            wing=wing_a, unit_number='A-402',
            defaults={
                'floor': 4,
                'unit_type': Unit.UnitType.BHK_3,
                'square_feet': 1650,
                'occupancy_status': Unit.OccupancyStatus.OWNER,
                'owner': resident_owner,
                'primary_resident': resident_owner,
                'parking_slot_number': 'P-A402',
                'intercom_extension': '1402',
            }
        )
        unit_a402.owner = resident_owner
        unit_a402.primary_resident = resident_owner
        unit_a402.occupancy_status = Unit.OccupancyStatus.OWNER
        unit_a402.save()

        unit_b201, _ = Unit.objects.get_or_create(
            wing=wing_b, unit_number='B-201',
            defaults={
                'floor': 2,
                'unit_type': Unit.UnitType.BHK_2,
                'square_feet': 1200,
                'occupancy_status': Unit.OccupancyStatus.TENANT,
                'owner': secretary_user,
                'primary_resident': resident_tenant,
                'parking_slot_number': 'P-B201',
                'intercom_extension': '1201',
            }
        )
        unit_b201.owner = secretary_user
        unit_b201.primary_resident = resident_tenant
        unit_b201.occupancy_status = Unit.OccupancyStatus.TENANT
        unit_b201.save()

        # Populate other units with authentic Indian owners, tenants, and vacant units
        owner_personas = [
            ('amitabh_s', 'Amitabh', 'Sen', 'amitabh.sen@example.com', '+91 98200 11221', 'Senior Financial Analyst'),
            ('sneha_j', 'Sneha', 'Joshi', 'sneha.joshi@example.com', '+91 98200 22332', 'Pediatric Surgeon'),
            ('rohan_m', 'Rohan', 'Mehta', 'rohan.mehta@example.com', '+91 98200 33443', 'Architect & Interior Designer'),
            ('meera_i', 'Meera', 'Iyer', 'meera.iyer@example.com', '+91 98200 44554', 'Professor of Mathematics'),
            ('sunil_v', 'Sunil', 'Verma', 'sunil.verma@example.com', '+91 98200 55665', 'Corporate Legal Counsel'),
            ('kavita_n', 'Kavita', 'Nair', 'kavita.nair@example.com', '+91 98200 66776', 'Senior HR Director'),
            ('aditya_k', 'Aditya', 'Kapoor', 'aditya.kapoor@example.com', '+91 98200 77887', 'Fintech Product Lead'),
            ('pooja_k', 'Pooja', 'Kulkarni', 'pooja.kulkarni@example.com', '+91 98200 88998', 'Executive VP - Banking'),
            ('deepak_s', 'Deepak', 'Singhania', 'deepak.singhania@example.com', '+91 98200 99009', 'Data Science Director'),
            ('nikhil_g', 'Nikhil', 'Gupta', 'nikhil.gupta@example.com', '+91 98200 10203', 'Investment Banker'),
        ]

        tenant_personas = [
            ('rahul_v', 'Rahul', 'Verma', 'rahul.verma@example.com', '+91 98200 30405', 'Senior UI/UX Designer'),
            ('tanvi_s', 'Tanvi', 'Shah', 'tanvi.shah@example.com', '+91 98200 40506', 'Management Consultant'),
            ('karan_d', 'Karan', 'Dave', 'karan.dave@example.com', '+91 98200 50607', 'Aerospace Engineer'),
            ('anjali_s', 'Anjali', 'Sharma', 'anjali.sharma@example.com', '+91 98200 60708', 'Biomedical Researcher'),
            ('harish_p', 'Harish', 'Patel', 'harish.patel@example.com', '+91 98200 70809', 'Digital Marketing Strategist'),
        ]

        owner_idx = 0
        tenant_idx = 0
        unit_counter = 0

        for w, prefix in [(wing_a, 'A'), (wing_b, 'B'), (wing_c, 'C')]:
            for flr in [1, 2, 3, 5, 7]:
                for num in [1, 2]:
                    u_num = f"{prefix}-{flr}0{num}"
                    if u_num not in ['A-402', 'B-201']:
                        unit_counter += 1
                        u_obj, _ = Unit.objects.get_or_create(
                            wing=w, unit_number=u_num,
                            defaults={
                                'floor': flr,
                                'unit_type': Unit.UnitType.BHK_3 if num == 2 else Unit.UnitType.BHK_2,
                                'square_feet': 1650 if num == 2 else 1250,
                                'parking_slot_number': f"P-{u_num}",
                                'intercom_extension': f"{flr}0{num}",
                            }
                        )
                        u_obj.floor = flr
                        u_obj.parking_slot_number = f"P-{u_num}"
                        u_obj.intercom_extension = f"{flr}0{num}"

        # 4. Vehicles with Indian Registration Plates
        Vehicle.objects.all().delete()
        veh_tata = Vehicle.objects.create(
            owner=resident_owner,
            unit=unit_a402,
            vehicle_type=Vehicle.VehicleType.EV_CAR,
            license_plate='MH-02-EG-8492',
            make_model='Tata Nexon EV Empowered (Midnight Teal)',
            parking_slot='P-A402',
            rfid_tag='RFID-EG-0492',
        )
        Vehicle.objects.create(
            owner=resident_tenant,
            unit=unit_b201,
            vehicle_type=Vehicle.VehicleType.CAR,
            license_plate='MH-02-AB-3109',
            make_model='Hyundai Creta SX (Pearl White)',
            parking_slot='P-B201',
            rfid_tag='RFID-EG-0319',
        )

        # 5. Domestic Helpers (Indian KYC records)
        DomesticStaff.objects.all().delete()
        maid = DomesticStaff.objects.create(
            name='Sunita Devi',
            role_type=DomesticStaff.StaffRole.MAID,
            phone_number='+91 98207 78901',
            passcode='4412',
            working_hours='07:30 AM - 03:00 PM',
        )
        maid.assigned_units.add(unit_a402, unit_b201)

        )
        maid.assigned_units.add(unit_a402, unit_b201)

        cook = DomesticStaff.objects.create(
            name='Rameshwar Singh',
            role_type=DomesticStaff.StaffRole.COOK,
            phone_number='+91 98207 78902',
            passcode='5523',
            working_hours='06:30 AM - 10:30 AM, 06:00 PM - 09:30 PM',
        )
        cook.assigned_units.add(unit_a402)

        driver = DomesticStaff.objects.create(
            name='Mahesh Yadav',
            role_type=DomesticStaff.StaffRole.DRIVER,
            phone_number='+91 98207 78903',
            passcode='6634',
            working_hours='08:00 AM - 08:00 PM',
        )
        driver.assigned_units.add(unit_a402)

        # 6. Bills & Payments
        today = timezone.now().date()
        current_month = date(today.year, today.month, 1)
        last_month = (current_month - timedelta(days=1)).replace(day=1)

        bill_past, _ = MaintenanceBill.objects.get_or_create(
            unit=unit_b201,
            billing_month=last_month,
            defaults={
                'bill_number': f"INV-{last_month.strftime('%Y%m')}-B201",
                'resident': resident_tenant,
                'due_date': last_month + timedelta(days=15),
                'base_charge': Decimal('4200.00'),
                'sinking_fund': Decimal('600.00'),
                'parking_charge': Decimal('300.00'),
                'water_charge': Decimal('400.00'),
                'amenity_charge': Decimal('500.00'),
                'total_amount': Decimal('6000.00'),
                'paid_amount': Decimal('6000.00'),
                'status': MaintenanceBill.Status.PAID,
                'paid_at': timezone.now() - timedelta(days=20),
            }
        )
        BillPayment.objects.get_or_create(
            bill=bill_past,
            defaults={
                'transaction_id': f"TXN-{last_month.strftime('%Y%m')}-B201-99",
                'receipt_number': f"RCPT-{last_month.strftime('%Y%m')}-0082",
                'payer': resident_tenant,
                'amount': Decimal('6000.00'),
                'payment_method': BillPayment.PaymentMethod.UPI,
            }
        )

        bill_current, _ = MaintenanceBill.objects.get_or_create(
            unit=unit_a402,
            billing_month=current_month,
            defaults={
                'bill_number': f"INV-{current_month.strftime('%Y%m')}-A402",
                'resident': resident_owner,
                'due_date': current_month + timedelta(days=15),
                'base_charge': Decimal('5775.00'),
                'sinking_fund': Decimal('825.00'),
                'parking_charge': Decimal('300.00'),
                'water_charge': Decimal('400.00'),
                'amenity_charge': Decimal('500.00'),
                'total_amount': Decimal('7800.00'),
                'paid_amount': Decimal('0.00'),
                'status': MaintenanceBill.Status.UNPAID,
            }
        )

        # 7. Amenities & Bookings
        MaintenanceBill.objects.get_or_create(
            unit=unit_b201,
            billing_month=current_month,
            defaults={
                'bill_number': f"INV-{current_month.strftime('%Y%m')}-B201",
                'resident': resident_tenant,
                'due_date': current_month + timedelta(days=15),
                'base_charge': Decimal('4200.00'),
                'sinking_fund': Decimal('600.00'),
                'parking_charge': Decimal('300.00'),
                'water_charge': Decimal('400.00'),
                'amenity_charge': Decimal('500.00'),
                'total_amount': Decimal('6000.00'),
                'paid_amount': Decimal('3000.00'),
                'status': MaintenanceBill.Status.PARTIAL,
            }
        )

        for title, category, amount, vendor, invoice in [
            ('Monthly common-area electricity', SocietyExpense.Category.ELECTRICITY, Decimal('48500.00'), 'MSEDCL', 'MSEDCL-SEP-2601'),
            ('Security guards and CCTV monitoring', SocietyExpense.Category.SECURITY, Decimal('72000.00'), 'ShieldGuard Facility Services', 'SGFS-2026-091'),
            ('Lift annual maintenance contract', SocietyExpense.Category.LIFT_AMC, Decimal('18500.00'), 'Otis India', 'OTIS-AMC-8842'),
            ('Monsoon plumbing repairs', SocietyExpense.Category.REPAIRS, Decimal('12750.00'), 'Patil Plumbing Works', 'PPW-1198'),
        ]:
            SocietyExpense.objects.get_or_create(
                invoice_number=invoice,
                defaults={
                    'title': title,
                    'category': category,
                    'amount': amount,
                    'expense_date': today - timedelta(days=3),
                    'vendor_name': vendor,
                    'approved_by': secretary_user,
                    'recorded_by': secretary_user,
                    'description': f'Indian society operations expense for Emerald Greens CHS Ltd. ({invoice}).',
                }
            )

        # 7. Amenities

        pool, _ = Amenity.objects.get_or_create(
            slug='olympic-infinity-pool',
            defaults={
                'name': 'Olympic Infinity Swimming Pool',
                'category': 'Wellness & Sports',
                'description': 'Temperature-controlled infinity lap pool with separate kids wading zone.',
                'capacity': 35,
                'hourly_rate': Decimal('0.00'),
            }
        )
        banquet, _ = Amenity.objects.get_or_create(
            slug='grand-banquet-hall',
            defaults={
                'name': 'Grand Imperial Banquet Hall',
                'category': 'Event & Party',
                'description': 'Air-conditioned luxury multipurpose hall equipped with JBL audio and catering pantry.',
                'capacity': 180,
                'hourly_rate': Decimal('1500.00'),
                'requires_approval': True,
            }
        )
        turf, _ = Amenity.objects.get_or_create(
            slug='box-cricket-turf',
            defaults={
                'name': 'Skyline Box Cricket & Football Turf',
                'category': 'Sports & Fitness',
                'description': 'All-weather floodlit FIFA-grade turf for box cricket and 5-a-side football.',
                'capacity': 20,
                'hourly_rate': Decimal('500.00'),
                'requires_approval': False,
            }
        )
        gym, _ = Amenity.objects.get_or_create(
            slug='fitness-studio',
            defaults={
                'name': 'Clubhouse Fitness Studio',
                'category': 'Wellness & Sports',
                'description': 'Residents-only gym with cardio, strength and yoga areas.',
                'capacity': 25,
                'hourly_rate': Decimal('0.00'),
                'location': 'Clubhouse First Floor',
            }
        )
        tennis, _ = Amenity.objects.get_or_create(
            slug='tennis-court',
            defaults={
                'name': 'Rooftop Tennis Court',
                'category': 'Sports',
                'description': 'Floodlit synthetic court for resident practice and coaching.',
                'capacity': 4,
                'hourly_rate': Decimal('250.00'),
                'location': 'Sports Arena Rooftop',
                'requires_approval': True,
            }
        )
        AmenityBooking.objects.all().delete()
        AmenityBooking.objects.create(
            amenity=banquet,
            resident=resident_owner,
            unit=unit_a402,
            booking_date=today + timedelta(days=2),
            start_time=time(17, 0),
            end_time=time(21, 0),
            guest_count=45,
            purpose='Family Birthday & Anniversary Celebration',
            total_fee=Decimal('6000.00'),
            status=AmenityBooking.Status.CONFIRMED,
        )
        AmenityBooking.objects.create(
            amenity=turf,
            resident=resident_tenant,
            unit=unit_b201,
            booking_date=today,
            start_time=time(19, 0),
            end_time=time(21, 0),
            guest_count=12,
            purpose='Weekend Box Cricket League',
            total_fee=Decimal('1000.00'),
            status=AmenityBooking.Status.CONFIRMED,
        )
        AmenityBooking.objects.get_or_create(
            amenity=tennis, resident=resident_tenant, unit=unit_b201,
            booking_date=today + timedelta(days=2), start_time=time(7, 0),
            defaults={'end_time': time(8, 0), 'guest_count': 2, 'purpose': 'Weekend tennis practice', 'total_fee': Decimal('250.00'), 'status': AmenityBooking.Status.CONFIRMED}
        )
        AmenityBooking.objects.get_or_create(
            amenity=pool, resident=resident_owner, unit=unit_a402,
            booking_date=today, start_time=time(17, 0),
            defaults={'end_time': time(18, 0), 'guest_count': 3, 'purpose': 'Family swim', 'total_fee': Decimal('0.00'), 'status': AmenityBooking.Status.CONFIRMED}
        )

        )

        # 7.1 Society Operating Expenses (Past 6 Months & Current Month)
        SocietyExpense.objects.all().delete()
        for i in range(5, -1, -1):
            m_num = today.month - i
            y_num = today.year
            while m_num <= 0:
                m_num += 12
                y_num -= 1
            exp_date = date(y_num, m_num, 10)
            
            SocietyExpense.objects.create(
                title=f'Tata Power Common Utility & Solar Grid Inverter Maintenance ({exp_date.strftime("%B %Y")})',
                category=SocietyExpense.Category.ELECTRICITY,
                amount=Decimal('42500.00'),
                expense_date=exp_date,
                vendor_name='Tata Power Distribution Ltd.',
                invoice_number=f'TP-{exp_date.strftime("%Y%m")}-9182',
                is_approved=True,
                approved_by=admin_user,
                recorded_by=secretary_user,
                description='Common area lighting, lift power, water pumping stations.',
            )
            SocietyExpense.objects.create(
                title=f'SIS Security Agency Guard Deployment Contract ({exp_date.strftime("%B %Y")})',
                category=SocietyExpense.Category.SECURITY,
                amount=Decimal('58000.00'),
                expense_date=exp_date + timedelta(days=2),
                vendor_name='Security & Intelligence Services (India) Ltd.',
                invoice_number=f'SIS-MUM-{exp_date.strftime("%Y%m")}-04',
                is_approved=True,
                approved_by=admin_user,
                recorded_by=secretary_user,
                description='24/7 Security supervision across Gate 1, Gate 2, and CCTV control hub.',
            )
            SocietyExpense.objects.create(
                title=f'Otis Elevator Comprehensive AMC & Inspection ({exp_date.strftime("%B %Y")})',
                category=SocietyExpense.Category.LIFT_AMC,
                amount=Decimal('18500.00'),
                expense_date=exp_date + timedelta(days=5),
                vendor_name='Otis Elevator Company (India) Ltd.',
                invoice_number=f'OTIS-AMC-{exp_date.strftime("%Y%m")}-22',
                is_approved=True,
                approved_by=admin_user,
                recorded_by=secretary_user,
                description='High-speed passenger elevator lubrication, rope tension test, emergency ARD test.',
            )
            SocietyExpense.objects.create(
                title=f'GreenRoots Landscaping & Swimming Pool Chlorination ({exp_date.strftime("%B %Y")})',
                category=SocietyExpense.Category.GARDENING,
                amount=Decimal('14000.00'),
                expense_date=exp_date + timedelta(days=7),
                vendor_name='GreenRoots Landscape Specialists',
                invoice_number=f'GR-LAND-{exp_date.strftime("%Y%m")}-11',
                is_approved=True,
                approved_by=admin_user,
                recorded_by=secretary_user,
                description='Weekly chemical filtration, pH balancing, lawn mowing, and tree pruning.',
            )

        # 8. EV Charging Stations & Solar Grid
        ev_st1, _ = EVChargingStation.objects.get_or_create(
            station_name='Station A-EV1 (Basement 1, Pole 14)',
            defaults={
                'power_kw': Decimal('22.0'),
                'connector_type': EVChargingStation.ConnectorType.TYPE_2,
                'location': 'Basement Level 1 - East Wing (Solar Grid)',
                'kwh_rate': Decimal('12.50'),
                'status': EVChargingStation.Status.AVAILABLE,
            }
        )
        ev_st2, _ = EVChargingStation.objects.get_or_create(
            station_name='Station B-DC Fast (Basement 2, Bay 8)',
            defaults={
                'power_kw': Decimal('50.0'),
                'connector_type': EVChargingStation.ConnectorType.CCS2,
                'location': 'Basement Level 2 - West Bay',
                'kwh_rate': Decimal('16.00'),
                'status': EVChargingStation.Status.AVAILABLE,
            }
        )
        EVChargingSession.objects.all().delete()
        EVChargingSession.objects.create(
            station=ev_st1,
            user=resident_owner,
            unit=unit_a402,
            vehicle=veh_tata,
            booking_date=today - timedelta(days=1),
            start_time=time(18, 0),
            end_time=time(20, 30),
            units_consumed_kwh=Decimal('32.50'),
            total_cost=Decimal('406.25'),
            status=EVChargingSession.SessionStatus.COMPLETED,
        )

        # 9. Move Requests with Indian Movers
        MoveInOutRequest.objects.all().delete()
        MoveInOutRequest.objects.create(
            unit=unit_b201,
            resident=resident_tenant,
            move_date=today + timedelta(days=4),
        MoveInOutRequest.objects.create(
            unit=unit_b201,
            resident=resident_tenant,
            move_date=today + timedelta(days=4),
            move_type=MoveInOutRequest.MoveType.RENOVATION,
            time_slot='Morning (08:00 AM - 12:00 PM)',
            service_lift_required=True,
            moving_company_name='Agarwal Packers & Movers (Powai)',
            vehicle_count=1,
            status=MoveInOutRequest.Status.APPROVED,
        )

        )

        # 10. Rule Violations
        RuleViolationReport.objects.all().delete()
        RuleViolationReport.objects.create(
            unit=unit_a402,
            reported_by=secretary_user,
            violation_type=RuleViolationReport.ViolationType.PARKING,
            description='Guest vehicle parked in designated EV charging bay on Saturday night.',
            status=RuleViolationReport.Status.RESOLVED,
            action_taken='Resident notified via intercom; vehicle repositioned to Visitor Bay 4.',
        )

        # 11. Lost & Found Items
        LostAndFoundItem.objects.all().delete()
        LostAndFoundItem.objects.create(
            item_name='BMW Car Smart Key FOB with Blue Lanyard',
            category=LostAndFoundItem.Category.KEYS,
            status=LostAndFoundItem.ItemStatus.FOUND,
            location='Near Clubhouse Swimming Pool Lounger',
            description='Found around 7 PM on Sunday. Deposited at Security Gate Desk #1.',
            reported_by=resident_owner,
            contact_phone='+91 98203 34567',
        )
        LostAndFoundItem.objects.create(
            item_name='Apple AirPods Pro (2nd Gen) in White Case',
            category=LostAndFoundItem.Category.ELECTRONICS,
            status=LostAndFoundItem.ItemStatus.LOST,
            location='Gym Treadmill #3 Area',
            description='Engraved with initials "VP" on backside of case.',
            reported_by=resident_tenant,
            contact_phone='+91 98204 45678',
        )

        )

        # 12. Society Documents (MahaRERA & MCS Act Compliance)
        SocietyDocument.objects.all().delete()
        SocietyDocument.objects.create(
            title='Emerald Greens CHS Ltd. Maharashtra Model Bye-Laws 2026',
            category=SocietyDocument.Category.BYELAWS,
            file_size_text='2.8 MB PDF',
            description='Complete constitution, membership voting rights, parking allocation guidelines, and share certificate terms.',
            uploaded_by=admin_user,
        )
        SocietyDocument.objects.create(
            title='Annual Fire Safety Audit & Municipal NOC Certificate (2026-2027)',
            category=SocietyDocument.Category.FIRE_NOC,
            file_size_text='1.4 MB PDF',
            description='Certified inspection of riser hydrant pipelines, smoke detectors, and emergency stairwell pressurized blowers by BMC Fire Dept.',
            uploaded_by=secretary_user,
        )

        # 13. Visitor Passes with Indian Names
        PreApprovedPass.objects.all().delete()
        PreApprovedPass.objects.create(
            pass_code='841920',
        PreApprovedPass.objects.all().delete()
        PreApprovedPass.objects.create(
            pass_code='841920',
            visitor_name='Rohan Mehta (Architect & Interior Designer)',
            visitor_phone='+91 98208 89012',
            unit=unit_a402,
            host_resident=resident_owner,
            valid_from=timezone.now(),
            valid_until=timezone.now() + timedelta(hours=12),
            purpose='Interior Renovation & Vastu Consultation',
            is_used=False,
        )

        )
        for name, phone, visitor_type, unit, purpose, status in [
            ('Rohan Mehta', '+91 98111 22334', VisitorLog.VisitorType.GUEST, unit_a402, 'Family dinner', VisitorLog.Status.INSIDE),
            ('Priya Nair', '+91 98222 33445', VisitorLog.VisitorType.DELIVERY, unit_b201, 'Grocery delivery', VisitorLog.Status.CHECKED_OUT),
            ('Suresh Patil', '+91 98333 44556', VisitorLog.VisitorType.SERVICE, unit_a402, 'AC servicing', VisitorLog.Status.INSIDE),
        ]:
            VisitorLog.objects.get_or_create(
                visitor_name=name, unit=unit, entry_time__date=today,
                defaults={'phone_number': phone, 'visitor_type': visitor_type, 'host_resident': unit.primary_resident, 'purpose': purpose, 'status': status, 'entry_guard': guard_user, 'is_pre_approved': status == VisitorLog.Status.INSIDE}
            )
        ParcelLog.objects.get_or_create(
            tracking_number='AMZ-MH-260901402',
            defaults={'unit': unit_a402, 'recipient_name': resident_owner.full_name, 'courier_company': ParcelLog.DeliveryCompany.AMAZON, 'guard': guard_user}
        )
        ParcelLog.objects.get_or_create(
            tracking_number='FKT-MH-260901201',
            defaults={'unit': unit_b201, 'recipient_name': resident_tenant.full_name, 'courier_company': ParcelLog.DeliveryCompany.FLIPKART, 'guard': guard_user}
        )

        for ticket_number, title, category, priority, status, unit, resident, assigned_staff in [
            ('TCK-2026-PLUMB1', 'Water seepage near kitchen sink', MaintenanceTicket.Category.PLUMBING, MaintenanceTicket.Priority.HIGH, MaintenanceTicket.Status.IN_PROGRESS, unit_a402, resident_owner, staff_electrician),
            ('TCK-2026-LIFT01', 'Lift B vibration on second floor', MaintenanceTicket.Category.ELEVATOR, MaintenanceTicket.Priority.URGENT, MaintenanceTicket.Status.OPEN, unit_b201, resident_tenant, None),
            ('TCK-2026-CCTV01', 'Intercom not connecting to main gate', MaintenanceTicket.Category.SECURITY, MaintenanceTicket.Priority.MEDIUM, MaintenanceTicket.Status.OPEN, unit_a402, resident_owner, staff_electrician),
        ]:
            MaintenanceTicket.objects.get_or_create(
                ticket_number=ticket_number,
                defaults={'title': title, 'category': category, 'priority': priority, 'status': status, 'unit': unit, 'resident': resident, 'assigned_staff': assigned_staff, 'description': f'Demo service request for Flat {unit.unit_number} at Emerald Greens CHS.'}
            )

        # 14. Gatekeeper Visitor Logs & Parcels
        VisitorLog.objects.all().delete()
        VisitorLog.objects.create(
            visitor_name='Amitabh Sen (Guest)',
            phone_number='+91 98209 12345',
            unit=unit_a402,
            host_resident=resident_owner,
            visitor_type=VisitorLog.VisitorType.GUEST,
            purpose='Family Dinner Visit',
            is_pre_approved=True,
            status=VisitorLog.Status.INSIDE,
            entry_guard=guard_user,
        )
        VisitorLog.objects.create(
            visitor_name='Rahul Verma (Swiggy Delivery)',
            phone_number='+91 98209 67890',
            unit=unit_b201,
            host_resident=resident_tenant,
            visitor_type=VisitorLog.VisitorType.DELIVERY,
            purpose='Food Delivery - Order #9910',
            status=VisitorLog.Status.CHECKED_OUT,
            entry_guard=guard_user,
        )

        ParcelLog.objects.all().delete()
        ParcelLog.objects.create(
            unit=unit_a402,
            recipient_name='Vikram Malhotra',
            courier_company=ParcelLog.DeliveryCompany.SWIGGY,
            tracking_number='BLK-MUM-8821',
            guard=guard_user,
            is_collected=False,
        )

        # 14. Notices & Polls
        Notice.objects.get_or_create(
            title='Ganesh Chaturthi General Body Meeting (2026) & Financial Audit Review',
            defaults={
                'notice_type': Notice.NoticeType.AGM,
                'author': admin_user,
                'is_pinned': True,
                'content': 'All members are requested to attend the society meeting at the clubhouse hall on Sunday at 10:30 AM.',
            }
        )

        poll, _ = SocietyPoll.objects.get_or_create(
            question='Should the society install 50kW rooftop solar panels with MSEDCL net metering?',
            defaults={
                'description': 'The project is expected to reduce the common-area electricity bill by approximately 68%.',
                'created_by': admin_user,
                'end_date': today + timedelta(days=10),
            }
        )

        )

        # 15. Helpdesk Service Tickets with SLA
        MaintenanceTicket.objects.all().delete()
        ticket1 = MaintenanceTicket.objects.create(
            unit=unit_a402,
            title='Tripping MCB in Master Bedroom AC Line',
            resident=resident_owner,
            category=MaintenanceTicket.Category.ELECTRICAL,
            priority=MaintenanceTicket.Priority.HIGH,
            description='The 32A Schneider MCB trips immediately when 2-ton inverter AC compressor kicks in.',
            assigned_staff=staff_electrician,
            status=MaintenanceTicket.Status.RESOLVED,
            resolution_notes='Replaced loose contactor relay and balanced phase load.',
            rating=5,
            resident_feedback='Mukesh arrived within 15 minutes and resolved the issue professionally.',
        )
        TicketComment.objects.create(
            ticket=ticket1,
            author=staff_electrician,
            message='Inspected the distribution board. Replaced faulty relay switch.'
        )

        ticket2 = MaintenanceTicket.objects.create(
            unit=unit_b201,
            title='Slow drainage in dry balcony floor trap',
            resident=resident_tenant,
            category=MaintenanceTicket.Category.PLUMBING,
            priority=MaintenanceTicket.Priority.MEDIUM,
            description='Water accumulates in the washing machine drain area.',
            assigned_staff=staff_electrician,
            status=MaintenanceTicket.Status.IN_PROGRESS,
        )

        # 16. Notices & AGM Polls
        Notice.objects.all().delete()
        Notice.objects.create(
            title='Annual General Body Meeting (AGM 2026) & Audited Balance Sheet Review',
            notice_type=Notice.NoticeType.AGM,
            author=admin_user,
            is_pinned=True,
            content='All registered members are requested to attend the Annual General Meeting at the Grand Banquet Hall on Sunday at 10:30 AM.',
        )
        Notice.objects.create(
            title='Overhead Water Tank UV Chlorination & Maintenance Schedule',
            notice_type=Notice.NoticeType.MAINTENANCE,
            author=secretary_user,
            is_pinned=False,
            content='Scheduled cleaning of overhead potable water tanks across Wing A, B & C on Saturday between 11:00 AM and 3:00 PM.',
        )

        SocietyPoll.objects.all().delete()
        poll = SocietyPoll.objects.create(
            question='Should Emerald Greens install a 50 kW Rooftop Solar Microgrid with Net-Metering?',
            description='Projected to reduce common area electricity utility bill by 68% and power the basement EV hyper-chargers.',
            created_by=admin_user,
            end_date=today + timedelta(days=10),
        )
        opt1 = PollOption.objects.create(poll=poll, option_text='Yes, approve solar microgrid installation')
        opt2 = PollOption.objects.create(poll=poll, option_text='No, defer to next financial year')
        PollVote.objects.create(poll=poll, user=admin_user, option=opt1)

        # 17. Community Forum Discussions
        DiscussionPost.objects.all().delete()
        post1 = DiscussionPost.objects.create(
            title='Proposal for Diwali Cultural Evening & Community Food Festival 2026',
            category=DiscussionPost.Category.EVENT,
            author=secretary_user,
            is_pinned=True,
            content='Dear Residents, we are planning a grand Diwali cultural evening with music, rangoli competitions, and a food fair at the Central Amphitheatre. Please share your suggestions and interest!',
        )
        DiscussionReply.objects.create(
            post=post1,
            author=resident_owner,
            message='Wonderful initiative! We would love to sponsor the sound stage and lighting for the event.',
        )
        DiscussionReply.objects.create(
            post=post1,
            author=resident_tenant,
            message='Count us in for organizing the kids dance performances!',
        )

        post2 = DiscussionPost.objects.create(
            title='Highly Recommending Dr. Anirudh Mehta (Visiting Pediatrician)',
            category=DiscussionPost.Category.RECOMMEND,
            author=resident_tenant,
            is_pinned=False,
            content='Sharing a great contact for parents: Dr. Anirudh Mehta visits Wing A on Tuesday and Friday evenings for child consultations.',
        )
        DiscussionReply.objects.create(
            post=post2,
            author=resident_owner,
            message='Thanks for sharing, Priya! Extremely helpful for our society families.',
        )

        self.stdout.write(self.style.SUCCESS('  [OK] Seeded Indian EV Charging, Helpdesk, Gatekeeper, Polls & Documents.'))

        self.stdout.write(self.style.SUCCESS('''
========================================================================
SmartSociety 360 - Complete Indian Enterprise System Seeded Successfully!

Pre-configured Demo Accounts (Authentic Indian Personas):
  * Admin / President : Rajesh Sharma   (User: admin            | Pass: admin123)
  * Hon. Secretary    : Ananya Deshmukh (User: secretary        | Pass: committee123)
  * Resident Owner    : Vikram Malhotra (User: john_doe         | Pass: resident123)
  * Resident Tenant   : Priya Patel     (User: sarah_smith      | Pass: resident123)
  * Security Guard    : Rajesh Gurjar   (User: guard_raj        | Pass: guard123)
  * Chief Technician  : Mukesh Sharma   (User: mike_electrician | Pass: staff123)

========================================================================
        '''))

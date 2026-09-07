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
    help = 'Seeds realistic demonstration data for SmartSociety 360'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting SmartSociety 360 data seeding...'))

        # 1. Maintenance Config
        config, _ = MaintenanceConfig.objects.get_or_create(
            id=1,
            defaults={
                'name': 'Emerald Greens CHS Ltd. Standard Billing Policy',
                'base_rate_per_sqft': Decimal('3.50'),
                'sinking_fund_rate': Decimal('0.50'),
                'fixed_amenities_fee': Decimal('500.00'),
                'parking_slot_fee': Decimal('300.00'),
                'water_fixed_charge': Decimal('400.00'),
                'late_fee_percentage': Decimal('2.00'),
                'payment_grace_days': 15,
            }
        )

        # 2. Key Users across all 5 roles
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@emeraldgreens.residence',
                'first_name': 'Amit',
                'last_name': 'Sharma',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'phone_number': '+91 98765 43210',
                'two_factor_enabled': True,
                'security_pin': '8899',
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        secretary_user, _ = User.objects.get_or_create(
            username='secretary',
            defaults={
                'email': 'secretary@emeraldgreens.residence',
                'first_name': 'Neha',
                'last_name': 'Deshmukh',
                'role': User.Role.COMMITTEE,
                'phone_number': '+91 98765 43211',
                'security_pin': '4455',
            }
        )
        secretary_user.set_password('committee123')
        secretary_user.save()

        resident_owner, _ = User.objects.get_or_create(
            username='john_doe',
            defaults={
                'email': 'amit.sharma@example.in',
                'first_name': 'Vikram',
                'last_name': 'Joshi',
                'role': User.Role.RESIDENT,
                'phone_number': '+91 98765 43212',
                'security_pin': '1234',
            }
        )
        resident_owner.set_password('resident123')
        resident_owner.save()
        ResidentProfile.objects.get_or_create(
            user=resident_owner,
            defaults={
                'resident_type': ResidentProfile.ResidentType.OWNER,
                'emergency_contact_name': 'Kavita Joshi',
                'emergency_contact_phone': '+91 98201 11223',
                'blood_group': 'O+',
                'occupation': 'Software Engineer',
                'intercom_number': '1402',
            }
        )

        resident_tenant, _ = User.objects.get_or_create(
            username='sarah_smith',
            defaults={
                'email': 'pooja.verma@example.in',
                'first_name': 'Pooja',
                'last_name': 'Verma',
                'role': User.Role.RESIDENT,
                'phone_number': '+91 98765 43213',
                'security_pin': '5678',
            }
        )
        resident_tenant.set_password('resident123')
        resident_tenant.save()
        ResidentProfile.objects.get_or_create(
            user=resident_tenant,
            defaults={
                'resident_type': ResidentProfile.ResidentType.TENANT,
                'emergency_contact_name': 'Rakesh Verma',
                'emergency_contact_phone': '+91 98202 22334',
                'blood_group': 'A+',
                'occupation': 'Chartered Accountant',
                'intercom_number': '1201',
            }
        )

        guard_user, _ = User.objects.get_or_create(
            username='guard_raj',
            defaults={
                'email': 'security.raj@emeraldgreens.residence',
                'first_name': 'Raj',
                'last_name': 'Patel',
                'role': User.Role.GUARD,
                'phone_number': '+91 98765 43214',
            }
        )
        guard_user.set_password('guard123')
        guard_user.save()

        staff_electrician, _ = User.objects.get_or_create(
            username='mike_electrician',
            defaults={
                'email': 'sanjay.pawar@emeraldgreens.residence',
                'first_name': 'Sanjay',
                'last_name': 'Pawar',
                'role': User.Role.STAFF,
                'phone_number': '+91 98765 43215',
            }
        )
        staff_electrician.set_password('staff123')
        staff_electrician.save()
        StaffProfile.objects.get_or_create(
            user=staff_electrician,
            defaults={
                'specialization': StaffProfile.Specialization.ELECTRICIAN,
                'badge_number': 'TECH-E-04',
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

        self.stdout.write(self.style.SUCCESS('  [OK] Created users & security profiles.'))

        # 3. Wings & Flats
        wing_a, _ = Wing.objects.get_or_create(name='Wing A - Sapphire Tower', defaults={'code': 'A', 'total_floors': 12})
        wing_b, _ = Wing.objects.get_or_create(name='Wing B - Emerald Crest', defaults={'code': 'B', 'total_floors': 12})
        wing_c, _ = Wing.objects.get_or_create(name='Wing C - Diamond Heights', defaults={'code': 'C', 'total_floors': 15})

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

        # Populate other units
        for w, prefix in [(wing_a, 'A'), (wing_b, 'B'), (wing_c, 'C')]:
            for flr in [1, 2, 3, 5, 7]:
                for num in [1, 2]:
                    u_num = f"{prefix}-{flr}0{num}"
                    if u_num not in ['A-402', 'B-201']:
                        Unit.objects.get_or_create(
                            wing=w, unit_number=u_num,
                            defaults={
                                'floor': flr,
                                'unit_type': random.choice([Unit.UnitType.BHK_2, Unit.UnitType.BHK_3, Unit.UnitType.BHK_1]),
                                'square_feet': random.choice([1100, 1350, 1500, 1750]),
                                'occupancy_status': random.choice([Unit.OccupancyStatus.OWNER, Unit.OccupancyStatus.TENANT, Unit.OccupancyStatus.VACANT]),
                                'parking_slot_number': f"P-{u_num}",
                                'intercom_extension': f"{flr}0{num}",
                            }
                        )

        # 4. Vehicles
        veh_tesla, _ = Vehicle.objects.get_or_create(
            license_plate='MH-02-EQ-8492',
            defaults={
                'owner': resident_owner,
                'unit': unit_a402,
                'vehicle_type': Vehicle.VehicleType.EV_CAR,
                'make_model': 'Tata Nexon EV (Glacier White)',
                'parking_slot': 'P-A402',
                'rfid_tag': 'RFID-EG-0492',
            }
        )
        Vehicle.objects.get_or_create(
            license_plate='MH-01-AB-3109',
            defaults={
                'owner': resident_tenant,
                'unit': unit_b201,
                'vehicle_type': Vehicle.VehicleType.CAR,
                'make_model': 'Maruti Suzuki Grand Vitara (Pearl White)',
                'parking_slot': 'P-B201',
                'rfid_tag': 'RFID-EG-0319',
            }
        )

        # 5. Domestic Helpers
        maid, _ = DomesticStaff.objects.get_or_create(
            name='Sunita Jadhav',
            defaults={
                'role_type': DomesticStaff.StaffRole.MAID,
                'phone_number': '+91 98765 43216',
                'passcode': '4412',
                'working_hours': '07:30 AM - 03:00 PM',
            }
        )
        maid.assigned_units.add(unit_a402, unit_b201)

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
                'gateway_reference': 'UPI-GPay-98421094',
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
                'description': 'Temperature-controlled infinity pool with separate children wading area.',
                'capacity': 35,
                'hourly_rate': Decimal('0.00'),
            }
        )
        banquet, _ = Amenity.objects.get_or_create(
            slug='grand-banquet-hall',
            defaults={
                'name': 'Grand Imperial Banquet Hall',
                'category': 'Event & Party',
                'description': 'Air-conditioned luxury multipurpose hall equipped with audio system and pantry.',
                'capacity': 180,
                'hourly_rate': Decimal('1500.00'),
                'requires_approval': True,
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
        AmenityBooking.objects.get_or_create(
            amenity=banquet, resident=resident_owner, unit=unit_a402,
            booking_date=today + timedelta(days=5), start_time=time(18, 0),
            defaults={'end_time': time(22, 0), 'guest_count': 65, 'purpose': 'Ganesh Chaturthi community gathering', 'total_fee': Decimal('6000.00'), 'status': AmenityBooking.Status.PENDING}
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

        # 8. EV Charging Stations
        ev_st1, _ = EVChargingStation.objects.get_or_create(
            station_name='Station A-EV1 (Basement 1, Pole 14)',
            defaults={
                'power_kw': Decimal('22.0'),
                'connector_type': EVChargingStation.ConnectorType.TYPE_2,
                'location': 'Basement Level 1 - East Wing',
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
        EVChargingSession.objects.get_or_create(
            station=ev_st1,
            user=resident_owner,
            unit=unit_a402,
            defaults={
                'vehicle': veh_tesla,
                'booking_date': today - timedelta(days=1),
                'start_time': time(18, 0),
                'end_time': time(20, 30),
                'units_consumed_kwh': Decimal('32.50'),
                'total_cost': Decimal('406.25'),
                'status': EVChargingSession.SessionStatus.COMPLETED,
            }
        )

        # 9. Move Requests
        MoveInOutRequest.objects.get_or_create(
            unit=unit_b201,
            resident=resident_tenant,
            move_date=today + timedelta(days=4),
            defaults={
                'move_type': MoveInOutRequest.MoveType.RENOVATION,
                'time_slot': 'Morning (08:00 AM - 12:00 PM)',
                'service_lift_required': True,
                    'moving_company_name': 'Mumbai Packers and Movers',
                'vehicle_count': 1,
                'status': MoveInOutRequest.Status.APPROVED,
            }
        )

        # 10. Rule Violations
        RuleViolationReport.objects.get_or_create(
            unit=unit_a402,
            reported_by=secretary_user,
            defaults={
                'violation_type': RuleViolationReport.ViolationType.PARKING,
                'description': 'Guest vehicle parked in designated handicap charging lane on Saturday night.',
                'status': RuleViolationReport.Status.RESOLVED,
                'action_taken': 'Resident notified via intercom; vehicle repositioned.',
            }
        )

        # 11. Lost & Found Items
        LostAndFoundItem.objects.get_or_create(
            item_name='Maruti Suzuki Car Key with Red Lanyard',
            defaults={
                'category': LostAndFoundItem.Category.KEYS,
                'status': LostAndFoundItem.ItemStatus.FOUND,
                'location': 'Near Clubhouse Swimming Pool Lounger',
                'description': 'Found around 7 PM on Sunday. Deposited at Security Gate Desk #1.',
                'reported_by': resident_owner,
                'contact_phone': '+91 98765 43212',
            }
        )
        LostAndFoundItem.objects.get_or_create(
            item_name='Boat Wireless Earbuds in Black Case',
            defaults={
                'category': LostAndFoundItem.Category.ELECTRONICS,
                'status': LostAndFoundItem.ItemStatus.LOST,
                'location': 'Gym Treadmill #3 Area',
                'description': 'Black case with initials "PV" written inside the lid.',
                'reported_by': resident_tenant,
                'contact_phone': '+91 98765 43213',
            }
        )

        # 12. Society Documents
        SocietyDocument.objects.get_or_create(
            title='Emerald Greens Cooperative Housing Society Model Bye-Laws 2026',
            defaults={
                'category': SocietyDocument.Category.BYELAWS,
                'file_size_text': '2.8 MB PDF',
                'description': 'Complete constitution, membership voting rights, parking allocation guidelines, and share certificate terms.',
                'uploaded_by': admin_user,
            }
        )
        SocietyDocument.objects.get_or_create(
            title='Annual Fire Safety Audit & Municipal NOC Certificate (2026-2027)',
            defaults={
                'category': SocietyDocument.Category.FIRE_NOC,
                'file_size_text': '1.4 MB PDF',
                'description': 'Certified inspection of riser hydrant pipelines, smoke detectors, and emergency stairwell pressurized blowers.',
                'uploaded_by': secretary_user,
            }
        )

        # 13. Visitor Passes
        PreApprovedPass.objects.get_or_create(
            pass_code='841920',
            defaults={
                'visitor_name': 'Amit Kulkarni (Architect)',
                'visitor_phone': '+91 99876 54321',
                'unit': unit_a402,
                'host_resident': resident_owner,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(hours=12),
                'purpose': 'Interior renovation consultation',
                'is_used': False,
            }
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
        opt1, _ = PollOption.objects.get_or_create(poll=poll, option_text='Yes, approve solar project immediately')
        opt2, _ = PollOption.objects.get_or_create(poll=poll, option_text='No, defer to next fiscal year')
        PollVote.objects.get_or_create(poll=poll, user=admin_user, defaults={'option': opt1})

        self.stdout.write(self.style.SUCCESS('  [OK] Seeded EV Charging, Move-in, Violations, Lost & Found, and Documents.'))

        self.stdout.write(self.style.SUCCESS('''
========================================================================
SmartSociety 360 - Complete Enterprise System Seeded Successfully!

Pre-configured Demo Accounts:
  * Admin / President : admin@emeraldgreens.residence   (Password: admin123)
  * Committee Member  : secretary@emeraldgreens.residence(Password: committee123)
    * Resident (Owner)  : amit.sharma@example.in          (Password: resident123)
    * Resident (Tenant) : pooja.verma@example.in          (Password: resident123)
  * Security Guard    : security.raj@emeraldgreens.residence (Password: guard123)
    * Facility Staff    : sanjay.pawar@emeraldgreens.residence (Password: staff123)
========================================================================
        '''))

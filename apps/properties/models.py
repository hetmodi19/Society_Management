from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Wing(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text=_("e.g., Wing A - Sapphire Tower"))
    code = models.CharField(max_length=10, unique=True, help_text=_("Short code e.g., A, B, C"))
    total_floors = models.PositiveIntegerField(default=10)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def units_count(self):
        return self.units.count()

    @property
    def occupied_units_count(self):
        return self.units.exclude(occupancy_status='VACANT').count()


class Unit(models.Model):
    class UnitType(models.TextChoices):
        STUDIO = 'STUDIO', _('Studio Apartment')
        BHK_1 = '1BHK', _('1 BHK Flat')
        BHK_2 = '2BHK', _('2 BHK Flat')
        BHK_3 = '3BHK', _('3 BHK Luxury Flat')
        BHK_4 = '4BHK', _('4 BHK Grand Flat')
        PENTHOUSE = 'PENTHOUSE', _('Sky Penthouse')
        VILLA = 'VILLA', _('Independent Villa')

    class OccupancyStatus(models.TextChoices):
        OWNER = 'OWNER', _('Owner Occupied')
        TENANT = 'TENANT', _('Tenant Occupied')
        VACANT = 'VACANT', _('Vacant / Unoccupied')

    wing = models.ForeignKey(Wing, on_delete=models.CASCADE, related_name='units')
    unit_number = models.CharField(max_length=20, help_text=_("e.g., A-101, B-402"))
    floor = models.PositiveIntegerField(default=1)
    unit_type = models.CharField(max_length=20, choices=UnitType.choices, default=UnitType.BHK_2)
    square_feet = models.PositiveIntegerField(default=1250, help_text=_("Carpet/Super built-up area in Sq. Ft."))
    occupancy_status = models.CharField(max_length=20, choices=OccupancyStatus.choices, default=OccupancyStatus.OWNER)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_units')
    primary_resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resident_flats')
    parking_slot_number = models.CharField(max_length=30, blank=True, null=True, help_text=_("e.g., P-A102"))
    intercom_extension = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('wing', 'unit_number')
        ordering = ['wing', 'floor', 'unit_number']

    def __str__(self):
        return f"{self.unit_number} ({self.wing.code}) - {self.get_unit_type_display()}"

    @property
    def display_name(self):
        return f"Flat {self.unit_number}"

    @property
    def is_owner_occupied(self):
        return self.occupancy_status == self.OccupancyStatus.OWNER

    @property
    def is_rented(self):
        return self.occupancy_status == self.OccupancyStatus.TENANT

    @property
    def is_vacant(self):
        return self.occupancy_status == self.OccupancyStatus.VACANT

    @property
    def occupancy_badge_label(self):
        if self.is_owner_occupied:
            return "Occupied"
        elif self.is_rented:
            return "Rented"
        return "Vacant"

    @property
    def occupancy_badge_class(self):
        if self.is_owner_occupied:
            return "badge-owner"
        elif self.is_rented:
            return "badge-tenant"
        return "badge-vacant"


class ResidentUnitMapping(models.Model):
    class Relation(models.TextChoices):
        OWNER = 'OWNER', _('Registered Owner')
        TENANT = 'TENANT', _('Tenant / Lease Holder')
        FAMILY = 'FAMILY', _('Family Member / Dependent')
        CO_OWNER = 'CO_OWNER', _('Co-Owner')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='unit_mappings')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='resident_mappings')
    relation_type = models.CharField(max_length=20, choices=Relation.choices, default=Relation.OWNER)
    is_primary = models.BooleanField(default=True)
    move_in_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.full_name} -> {self.unit.unit_number} ({self.get_relation_type_display()})"


class Vehicle(models.Model):
    class VehicleType(models.TextChoices):
        CAR = 'CAR', _('Four Wheeler (Car/SUV)')
        EV_CAR = 'EV_CAR', _('Electric Car (EV)')
        MOTORCYCLE = 'MOTORCYCLE', _('Two Wheeler / Motorcycle')
        EV_SCOOTER = 'EV_SCOOTER', _('Electric Scooter / Bike')
        BICYCLE = 'BICYCLE', _('Bicycle')

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicles')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.choices, default=VehicleType.CAR)
    license_plate = models.CharField(max_length=30, unique=True, help_text=_("e.g., MH-02-AB-1234 or NY-5849-ZZ"))
    make_model = models.CharField(max_length=100, help_text=_("e.g., Honda Civic Silver, Tesla Model 3"))
    parking_slot = models.CharField(max_length=30, blank=True)
    rfid_tag = models.CharField(max_length=50, blank=True, null=True, unique=True)
    is_active = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.license_plate} - {self.make_model} ({self.unit.unit_number})"


class DomesticStaff(models.Model):
    class StaffRole(models.TextChoices):
        MAID = 'MAID', _('Housekeeper / Maid')
        COOK = 'COOK', _('Chef / Cook')
        DRIVER = 'DRIVER', _('Personal Driver')
        NANNY = 'NANNY', _('Nanny / Babysitter')
        CLEANER = 'CLEANER', _('Car Cleaner')
        TUTOR = 'TUTOR', _('Home Tutor')
        OTHER = 'OTHER', _('Other Daily Helper')

    name = models.CharField(max_length=100)
    role_type = models.CharField(max_length=30, choices=StaffRole.choices, default=StaffRole.MAID)
    phone_number = models.CharField(max_length=20)
    passcode = models.CharField(max_length=10, unique=True, help_text=_("Gate quick check-in 4-digit code"))
    assigned_units = models.ManyToManyField(Unit, related_name='domestic_staff_members', blank=True)
    is_verified = models.BooleanField(default=True)
    profile_photo = models.ImageField(upload_to='staff/helpers/', blank=True, null=True)
    working_hours = models.CharField(max_length=100, default="08:00 AM - 04:00 PM")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_role_type_display()}) - Code: {self.passcode}"


class MoveInOutRequest(models.Model):
    class MoveType(models.TextChoices):
        MOVE_IN = 'MOVE_IN', _('Moving In (New Resident/Tenant)')
        MOVE_OUT = 'MOVE_OUT', _('Moving Out (Relocation)')
        RENOVATION = 'RENOVATION', _('Heavy Furniture / Interior Fit-Out')

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending Security Review')
        APPROVED = 'APPROVED', _('Approved & Slot Reserved')
        COMPLETED = 'COMPLETED', _('Completed')
        REJECTED = 'REJECTED', _('Rejected')

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='move_requests')
    resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='move_requests')
    move_type = models.CharField(max_length=20, choices=MoveType.choices, default=MoveType.MOVE_IN)
    move_date = models.DateField()
    time_slot = models.CharField(max_length=50, default='Morning (09:00 AM - 01:00 PM)')
    service_lift_required = models.BooleanField(default=True, help_text=_('Reserve Service Elevator'))
    moving_company_name = models.CharField(max_length=100, blank=True)
    vehicle_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    security_deposit_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-move_date']

    def __str__(self):
        return f"{self.get_move_type_display()} for Flat {self.unit.unit_number} on {self.move_date}"


class RuleViolationReport(models.Model):
    class ViolationType(models.TextChoices):
        PARKING = 'PARKING', _('Unauthorized / Blocked Parking')
        NOISE = 'NOISE', _('Late Night Noise / Loud Music')
        PETS = 'PETS', _('Pet Policy / Common Area Mess')
        TRASH = 'TRASH', _('Improper Waste / Balcony Littering')
        CORRIDOR = 'CORRIDOR', _('Corridor Obstruction / Shoe Racks')
        OTHER = 'OTHER', _('Other Society Rule Infraction')

    class Status(models.TextChoices):
        REPORTED = 'REPORTED', _('Reported')
        UNDER_REVIEW = 'UNDER_REVIEW', _('Under Committee Review')
        NOTICE_ISSUED = 'NOTICE_ISSUED', _('Warning / Fine Issued')
        RESOLVED = 'RESOLVED', _('Resolved / Closed')

    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_violations')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='rule_violations', help_text=_('Flat involved in violation'))
    violation_type = models.CharField(max_length=30, choices=ViolationType.choices, default=ViolationType.PARKING)
    description = models.TextField()
    evidence_photo = models.ImageField(upload_to='violations/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REPORTED)
    action_taken = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Violation [{self.get_violation_type_display()}] against Flat {self.unit.unit_number}"

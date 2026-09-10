from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Society Super Admin / President')
        SECRETARY = 'SECRETARY', _('Hon. Secretary')
        TREASURER = 'TREASURER', _('Hon. Treasurer')
        ACCOUNTANT = 'ACCOUNTANT', _('Society Accountant')
        COMMITTEE = 'COMMITTEE', _('Management Committee Member')
        FACILITY_MGR = 'FACILITY_MGR', _('Facility Manager')
        OWNER = 'OWNER', _('Flat Owner (Resident)')
        TENANT = 'TENANT', _('Tenant / Rented Person')
        RESIDENT = 'RESIDENT', _('Resident Member')
        GUARD = 'GUARD', _('Security Guard / Gatekeeper')
        STAFF = 'STAFF', _('Maintenance Staff / Technician')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RESIDENT,
        help_text=_('User role determines permissions and dashboard layout.')
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/avatars/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=True, help_text=_('Account verified by society admin.'))
    two_factor_enabled = models.BooleanField(default=False, help_text=_('Require 2FA PIN on login'))
    security_pin = models.CharField(max_length=6, default='1234', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.username

    @property
    def initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.username:
            return self.username[:2].upper()
        return "SM"

    @property
    def is_society_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_secretary(self):
        return self.role in [self.Role.ADMIN, self.Role.SECRETARY] or self.is_superuser

    @property
    def is_treasurer(self):
        return self.role in [self.Role.ADMIN, self.Role.TREASURER, self.Role.ACCOUNTANT] or self.is_superuser

    @property
    def is_accountant(self):
        return self.role in [self.Role.ADMIN, self.Role.TREASURER, self.Role.ACCOUNTANT] or self.is_superuser

    @property
    def is_financial_manager(self):
        return self.role in [self.Role.ADMIN, self.Role.TREASURER, self.Role.ACCOUNTANT] or self.is_superuser

    @property
    def is_facility_manager(self):
        return self.role in [self.Role.ADMIN, self.Role.FACILITY_MGR] or self.is_superuser

    @property
    def is_committee_member(self):
        return self.role in [
            self.Role.ADMIN,
            self.Role.SECRETARY,
            self.Role.TREASURER,
            self.Role.ACCOUNTANT,
            self.Role.COMMITTEE,
            self.Role.FACILITY_MGR
        ] or self.is_superuser

    @property
    def is_flat_owner(self):
        if self.role == self.Role.OWNER:
            return True
        if self.role == self.Role.RESIDENT and hasattr(self, 'resident_profile') and self.resident_profile.resident_type == 'OWNER':
            return True
        if self.owned_units.exists():
            return True
        return False

    @property
    def is_tenant(self):
        if self.role == self.Role.TENANT:
            return True
        if self.role == self.Role.RESIDENT and hasattr(self, 'resident_profile') and self.resident_profile.resident_type == 'TENANT':
            return True
        return False

    @property
    def is_resident_user(self):
        return self.role in [self.Role.OWNER, self.Role.TENANT, self.Role.RESIDENT] or self.is_flat_owner or self.is_tenant

    @property
    def is_security_guard(self):
        return self.role == self.Role.GUARD

    @property
    def is_facility_staff(self):
        return self.role in [self.Role.STAFF, self.Role.FACILITY_MGR]

    def has_permission(self, perm_code):
        from .permissions import has_perm
        return has_perm(self, perm_code)

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"


class ResidentProfile(models.Model):
    class ResidentType(models.TextChoices):
        OWNER = 'OWNER', _('Property Owner')
        TENANT = 'TENANT', _('Tenant / Renter')
        FAMILY = 'FAMILY', _('Family Member')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resident_profile')
    resident_type = models.CharField(max_length=20, choices=ResidentType.choices, default=ResidentType.OWNER)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=10, blank=True, default='Unknown')
    occupation = models.CharField(max_length=100, blank=True)
    intercom_number = models.CharField(max_length=10, blank=True)
    move_in_date = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Resident Profile: {self.user.full_name} ({self.get_resident_type_display()})"


class StaffProfile(models.Model):
    class Specialization(models.TextChoices):
        ELECTRICIAN = 'ELECTRICIAN', _('Electrician')
        PLUMBER = 'PLUMBER', _('Plumber')
        CARPENTER = 'CARPENTER', _('Carpenter')
        LIFT_TECH = 'LIFT_TECH', _('Lift & Elevator Specialist')
        GARDENER = 'GARDENER', _('Gardener / Landscaping')
        HOUSEKEEPING = 'HOUSEKEEPING', _('Housekeeping / Cleaning')
        SECURITY_CHIEF = 'SECURITY_CHIEF', _('Security Supervisor')
        GENERAL = 'GENERAL', _('General Maintenance')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    specialization = models.CharField(max_length=30, choices=Specialization.choices, default=Specialization.GENERAL)
    badge_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    duty_shift = models.CharField(max_length=50, default='Morning (08:00 - 16:00)')
    is_on_duty = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.8)

    def __str__(self):
        return f"Staff: {self.user.full_name} - {self.get_specialization_display()}"


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_records')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, default='Desktop Browser')
    timestamp = models.DateTimeField(default=timezone.now)
    is_successful = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Login Histories'

    def __str__(self):
        return f"{self.user.username} logged in from {self.ip_address} on {self.timestamp.strftime('%d %b %H:%M')}"

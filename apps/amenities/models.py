from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, time

class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text=_("e.g. Grand Banquet Hall, Infinity Pool, Squash Court"))
    slug = models.SlugField(max_length=100, unique=True)
    category = models.CharField(max_length=50, default='Recreation', help_text=_("Sports, Wellness, Event, Leisure"))
    description = models.TextField()
    capacity = models.PositiveIntegerField(default=50, help_text=_("Maximum guests allowed"))
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text=_("₹0 for free amenities like Gym/Pool"))
    location = models.CharField(max_length=100, default='Clubhouse Ground Floor')
    open_time = models.TimeField(default=time(6, 0))
    close_time = models.TimeField(default=time(22, 0))
    rules = models.TextField(blank=True, help_text=_("Guidelines, dress code, cleaning deposit terms."))
    photo = models.ImageField(upload_to='amenities/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Amenities'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Rate: ₹{self.hourly_rate}/hr)"


class AmenityBooking(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        PENDING = 'PENDING', _('Pending Approval')
        CANCELLED = 'CANCELLED', _('Cancelled')
        REJECTED = 'REJECTED', _('Rejected')

    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE, related_name='bookings')
    resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='amenity_bookings')
    unit = models.ForeignKey('properties.Unit', on_delete=models.CASCADE, related_name='unit_amenity_bookings')
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    guest_count = models.PositiveIntegerField(default=1)
    purpose = models.CharField(max_length=200, blank=True, help_text=_("e.g. Birthday Party, Yoga session"))
    total_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    rejection_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-booking_date', '-start_time']

    def __str__(self):
        return f"{self.amenity.name} on {self.booking_date} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}) by {self.resident.full_name}"


class EVChargingStation(models.Model):
    class ConnectorType(models.TextChoices):
        TYPE_2 = 'TYPE_2', _('Type 2 AC (Fast 7.4 kW - 22 kW)')
        CCS2 = 'CCS2', _('CCS2 DC Fast Charger (50 kW)')
        CHAdeMO = 'CHAdeMO', _('CHAdeMO DC Fast (50 kW)')
        SOCKET_15A = 'SOCKET_15A', _('15A Standard 3-Pin Socket')

    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', _('Available')
        CHARGING = 'CHARGING', _('Currently In Use / Charging')
        MAINTENANCE = 'MAINTENANCE', _('Under Maintenance')

    station_name = models.CharField(max_length=100, help_text=_("e.g. Station A-EV1 (Basement 1, Pole 14)"))
    power_kw = models.DecimalField(max_digits=5, decimal_places=1, default=7.4, help_text=_("Capacity in kW"))
    connector_type = models.CharField(max_length=30, choices=ConnectorType.choices, default=ConnectorType.TYPE_2)
    location = models.CharField(max_length=100, default='Basement Level 1 - Bay EV')
    kwh_rate = models.DecimalField(max_digits=6, decimal_places=2, default=12.50, help_text=_("Cost per kWh (₹)"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.station_name} ({self.power_kw}kW) - ₹{self.kwh_rate}/kWh"


class EVChargingSession(models.Model):
    class SessionStatus(models.TextChoices):
        RESERVED = 'RESERVED', _('Slot Reserved')
        ACTIVE = 'ACTIVE', _('Charging in Progress')
        COMPLETED = 'COMPLETED', _('Completed / Billed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    station = models.ForeignKey(EVChargingStation, on_delete=models.CASCADE, related_name='sessions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ev_sessions')
    unit = models.ForeignKey('properties.Unit', on_delete=models.CASCADE, related_name='ev_charges')
    vehicle = models.ForeignKey('properties.Vehicle', on_delete=models.SET_NULL, null=True, blank=True)
    booking_date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    units_consumed_kwh = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=SessionStatus.choices, default=SessionStatus.RESERVED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-booking_date', '-start_time']

    def __str__(self):
        return f"EV Session @ {self.station.station_name} for {self.user.full_name} ({self.booking_date})"

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import random

def generate_passcode():
    return str(random.randint(100000, 999999))

class VisitorLog(models.Model):
    class VisitorType(models.TextChoices):
        GUEST = 'GUEST', _('Guest / Family Friend')
        DELIVERY = 'DELIVERY', _('Delivery Agent (Amazon, Food, Courier)')
        CAB = 'CAB', _('Cab / Taxi (Uber, Ola, Lyft)')
        SERVICE = 'SERVICE', _('Service Technician / Contractor')
        INTERVIEW = 'INTERVIEW', _('Official / Interview / Business')
        OTHER = 'OTHER', _('Other Visitor')

    class Status(models.TextChoices):
        INSIDE = 'INSIDE', _('Currently Inside Society')
        CHECKED_OUT = 'CHECKED_OUT', _('Checked Out / Departed')
        DENIED = 'DENIED', _('Entry Denied by Resident / Guard')

    visitor_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    visitor_type = models.CharField(max_length=20, choices=VisitorType.choices, default=VisitorType.GUEST)
    unit = models.ForeignKey('properties.Unit', on_delete=models.CASCADE, related_name='visitors')
    host_resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='hosted_visitors')
    vehicle_number = models.CharField(max_length=30, blank=True, null=True, help_text=_("Visitor Vehicle (if any)"))
    purpose = models.CharField(max_length=200, blank=True)
    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INSIDE)
    is_pre_approved = models.BooleanField(default=False)
    entry_guard = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='guard_checked_entries')

    class Meta:
        ordering = ['-entry_time']

    def __str__(self):
        return f"{self.visitor_name} ({self.get_visitor_type_display()}) -> Flat {self.unit.unit_number}"

    def checkout(self):
        self.exit_time = timezone.now()
        self.status = self.Status.CHECKED_OUT
        self.save()


class PreApprovedPass(models.Model):
    pass_code = models.CharField(max_length=10, unique=True, default=generate_passcode)
    visitor_name = models.CharField(max_length=100)
    visitor_phone = models.CharField(max_length=20, blank=True)
    unit = models.ForeignKey('properties.Unit', on_delete=models.CASCADE, related_name='preapproved_passes')
    host_resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='issued_passes')
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    purpose = models.CharField(max_length=200, default='Personal Visit')
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Pass #{self.pass_code} for {self.visitor_name} (Flat {self.unit.unit_number})"

    @property
    def is_expired(self):
        return timezone.now() > self.valid_until


class ParcelLog(models.Model):
    class DeliveryCompany(models.TextChoices):
        AMAZON = 'AMAZON', _('Amazon')
        FLIPKART = 'FLIPKART', _('Flipkart')
        SWIGGY = 'SWIGGY', _('Swiggy / Instamart')
        ZOMATO = 'ZOMATO', _('Zomato / Blinkit')
        DHL = 'DHL', _('DHL / BlueDart')
        FEDEX = 'FEDEX', _('FedEx / Delhivery')
        OTHER = 'OTHER', _('Other Courier')

    unit = models.ForeignKey('properties.Unit', on_delete=models.CASCADE, related_name='parcels')
    recipient_name = models.CharField(max_length=100)
    courier_company = models.CharField(max_length=30, choices=DeliveryCompany.choices, default=DeliveryCompany.AMAZON)
    tracking_number = models.CharField(max_length=100, blank=True)
    received_at = models.DateTimeField(default=timezone.now)
    collected_at = models.DateTimeField(null=True, blank=True)
    is_collected = models.BooleanField(default=False)
    collected_by = models.CharField(max_length=100, blank=True)
    guard = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-received_at']

    def __str__(self):
        return f"Parcel for Flat {self.unit.unit_number} ({self.get_courier_company_display()})"


class SOSAlert(models.Model):
    class AlertType(models.TextChoices):
        MEDICAL = 'MEDICAL', _('Medical Emergency / Ambulance')
        FIRE = 'FIRE', _('Fire Alarm / Smoke Hazard')
        SECURITY = 'SECURITY', _('Security Breach / Intruder')
        ELEVATOR = 'ELEVATOR', _('Elevator / Lift Stuck')
        GAS_LEAK = 'GAS_LEAK', _('LPG Gas Leakage Alert')
        OTHER = 'OTHER', _('General Urgent Alert')

    alert_type = models.CharField(max_length=30, choices=AlertType.choices, default=AlertType.MEDICAL)
    triggered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='triggered_sos_alerts')
    unit = models.ForeignKey('properties.Unit', on_delete=models.SET_NULL, null=True, blank=True, related_name='sos_alerts')
    location_details = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_sos_alerts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"SOS [{self.get_alert_type_display()}] by {self.triggered_by.full_name} at {self.created_at.strftime('%H:%M')}"

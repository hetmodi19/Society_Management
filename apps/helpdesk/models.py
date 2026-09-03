from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

class MaintenanceTicket(models.Model):
    class Category(models.TextChoices):
        PLUMBING = 'PLUMBING', _('Plumbing / Water Leakage')
        ELECTRICAL = 'ELECTRICAL', _('Electrical / Power Issue')
        ELEVATOR = 'ELEVATOR', _('Elevator / Lift Malfunction')
        CARPENTRY = 'CARPENTRY', _('Carpentry / Doors & Windows')
        PEST_CONTROL = 'PEST_CONTROL', _('Pest Control & Fumigation')
        SECURITY = 'SECURITY', _('Security / Intercom / CCTV')
        COMMON_AREA = 'COMMON_AREA', _('Common Area Lighting / Cleaning')
        GARDEN = 'GARDEN', _('Gardening & Lawns')
        OTHER = 'OTHER', _('General / Other Service Request')

    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low (Routine request)')
        MEDIUM = 'MEDIUM', _('Medium (Standard)')
        HIGH = 'HIGH', _('High (Important)')
        URGENT = 'URGENT', _('Urgent (Immediate Attention Needed)')

    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open / Logged')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress / Assigned')
        RESOLVED = 'RESOLVED', _('Resolved / Completed')
        CLOSED = 'CLOSED', _('Closed')

    ticket_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.PLUMBING)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)

    resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='raised_tickets')
    unit = models.ForeignKey('properties.Unit', on_delete=models.CASCADE, related_name='maintenance_tickets')
    assigned_staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')

    description = models.TextField()
    photo = models.ImageField(upload_to='helpdesk/tickets/', blank=True, null=True)

    resolution_notes = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text=_("Resident 1 to 5 star rating"))
    resident_feedback = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket_number}: {self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            year = timezone.now().year
            rand_id = uuid.uuid4().hex[:6].upper()
            self.ticket_number = f"TCK-{year}-{rand_id}"
        super().save(*args, **kwargs)


class TicketComment(models.Model):
    ticket = models.ForeignKey(MaintenanceTicket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(upload_to='helpdesk/comments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.full_name} on {self.ticket.ticket_number}"

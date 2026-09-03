"""
Global template context processor for SmartSociety 360.
"""
from django.conf import settings

def society_context(request):
    """Provide society global information and user status to all templates."""
    context = {
        'SOCIETY_NAME': getattr(settings, 'SOCIETY_NAME', 'SmartSociety 360'),
        'SOCIETY_CODE': getattr(settings, 'SOCIETY_CODE', 'SS-360'),
        'SOCIETY_ADDRESS': getattr(settings, 'SOCIETY_ADDRESS', 'Palm Boulevard, Skyline District'),
        'SOCIETY_CITY': getattr(settings, 'SOCIETY_CITY', 'Metro City'),
        'SOCIETY_CONTACT': getattr(settings, 'SOCIETY_CONTACT', '+1 (800) 555-SOCIETY'),
        'unread_notices_count': 0,
        'pending_tickets_count': 0,
        'unpaid_bills_count': 0,
        'active_sos_alerts': [],
    }

    if request.user.is_authenticated:
        try:
            from apps.communications.models import Notice, EmergencyAlert
            from apps.helpdesk.models import MaintenanceTicket
            from apps.billing.models import MaintenanceBill
            from apps.gatekeeper.models import SOSAlert

            # Active SOS alerts in society (last 24h unresolved)
            context['active_sos_alerts'] = SOSAlert.objects.filter(is_resolved=False).order_by('-created_at')[:3]

            # Pending tickets
            if request.user.role in ['ADMIN', 'COMMITTEE', 'STAFF']:
                context['pending_tickets_count'] = MaintenanceTicket.objects.filter(status__in=['OPEN', 'IN_PROGRESS']).count()
            else:
                context['pending_tickets_count'] = MaintenanceTicket.objects.filter(resident=request.user, status__in=['OPEN', 'IN_PROGRESS']).count()

            # Unpaid bills
            if request.user.role in ['ADMIN', 'COMMITTEE']:
                context['unpaid_bills_count'] = MaintenanceBill.objects.filter(status__in=['UNPAID', 'OVERDUE']).count()
            elif request.user.role == 'RESIDENT':
                # Bills for resident flats
                flats = request.user.resident_flats.all()
                context['unpaid_bills_count'] = MaintenanceBill.objects.filter(unit__in=flats, status__in=['UNPAID', 'OVERDUE']).count()

            # Emergency pinned notices
            context['urgent_notices'] = Notice.objects.filter(is_pinned=True, is_active=True).order_by('-created_at')[:2]

        except Exception:
            # During migrations or setup before tables exist
            pass

    return context

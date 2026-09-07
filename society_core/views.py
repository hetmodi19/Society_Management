from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta, date

from apps.properties.models import Unit, Wing, Vehicle, DomesticStaff
from apps.billing.models import MaintenanceBill, BillPayment, SocietyExpense
from apps.gatekeeper.models import VisitorLog, PreApprovedPass, ParcelLog, SOSAlert
from apps.helpdesk.models import MaintenanceTicket
from apps.amenities.models import Amenity, AmenityBooking
from apps.communications.models import Notice, SocietyPoll, PollVote

def landing_page_view(request):
    """Public luxury building website showcasing Emerald Greens residences, amenities & smart society portal."""
    try:
        total_flats = Unit.objects.count()
        occupied_flats = Unit.objects.exclude(occupancy_status=Unit.OccupancyStatus.VACANT).count()
        wings_count = Wing.objects.count()
    except Exception:
        total_flats = 120
        occupied_flats = 114
        wings_count = 2

    try:
        from apps.amenities.models import EVChargingStation
        active_amenities = list(Amenity.objects.filter(is_active=True))
        ev_chargers_count = EVChargingStation.objects.filter(is_active=True).count()
    except Exception:
        active_amenities = []
        ev_chargers_count = 6

    try:
        pinned_notices = list(Notice.objects.filter(is_pinned=True, is_active=True).order_by('-created_at')[:3])
    except Exception:
        pinned_notices = []

    try:
        today = timezone.now().date()
        active_poll = SocietyPoll.objects.filter(is_active=True, end_date__gte=today).first()
    except Exception:
        active_poll = None

    return render(request, 'landing.html', {
        'total_flats': total_flats or 120,
        'occupied_flats': occupied_flats or 114,
        'wings_count': wings_count or 2,
        'active_amenities': active_amenities,
        'ev_chargers_count': ev_chargers_count or 6,
        'pinned_notices': pinned_notices,
        'active_poll': active_poll,
    })


@login_required
def dashboard_view(request):
    """Role-aware intelligent society management dashboard."""
    user = request.user
    today = timezone.now().date()

    # Route guard directly to gate terminal if desired, or show guard view
    if user.role == 'GUARD':
        return redirect('gatekeeper:terminal')

    # Common metrics
    pinned_notices = Notice.objects.filter(is_pinned=True, is_active=True)[:3]
    active_poll = SocietyPoll.objects.filter(is_active=True, end_date__gte=today).first()
    has_voted_active_poll = active_poll.user_has_voted(user) if active_poll else False
    active_sos_alerts = SOSAlert.objects.filter(is_resolved=False)[:3]

    # --- ADMIN & COMMITTEE VIEW ---
    if user.is_society_admin or user.is_committee_member:
        total_units = Unit.objects.count()
        occupied_units = Unit.objects.exclude(occupancy_status=Unit.OccupancyStatus.VACANT).count()
        vacant_units = total_units - occupied_units
        occupancy_rate = round((occupied_units / total_units * 100) if total_units > 0 else 0, 1)

        # Financials for current month
        first_of_month = date(today.year, today.month, 1)
        month_bills = MaintenanceBill.objects.filter(billing_month=first_of_month)
        monthly_billed = month_bills.aggregate(t=Sum('total_amount'))['t'] or 0
        monthly_collected = month_bills.aggregate(t=Sum('paid_amount'))['t'] or 0
        monthly_pending = monthly_billed - monthly_collected
        collection_percentage = round((monthly_collected / monthly_billed * 100) if monthly_billed > 0 else 0, 1)

        # Total society reserves
        total_income = BillPayment.objects.filter(payment_status=BillPayment.PaymentStatus.SUCCESS).aggregate(t=Sum('amount'))['t'] or 0
        total_expense = SocietyExpense.objects.filter(is_approved=True).aggregate(t=Sum('amount'))['t'] or 0
        net_reserve = total_income - total_expense

        # Security & Helpdesk stats
        active_visitors_count = VisitorLog.objects.filter(status=VisitorLog.Status.INSIDE).count()
        open_tickets = MaintenanceTicket.objects.filter(status=MaintenanceTicket.Status.OPEN).count()
        in_progress_tickets = MaintenanceTicket.objects.filter(status=MaintenanceTicket.Status.IN_PROGRESS).count()
        today_bookings = AmenityBooking.objects.filter(booking_date=today, status=AmenityBooking.Status.CONFIRMED).count()

        recent_tickets = MaintenanceTicket.objects.select_related('unit', 'resident').order_by('-created_at')[:5]
        recent_visitors = VisitorLog.objects.select_related('unit').order_by('-entry_time')[:5]

        return render(request, 'dashboard/admin_dashboard.html', {
            'total_units': total_units,
            'occupied_units': occupied_units,
            'vacant_units': vacant_units,
            'occupancy_rate': occupancy_rate,
            'monthly_billed': monthly_billed,
            'monthly_collected': monthly_collected,
            'monthly_pending': monthly_pending,
            'collection_percentage': collection_percentage,
            'net_reserve': net_reserve,
            'active_visitors_count': active_visitors_count,
            'open_tickets': open_tickets,
            'in_progress_tickets': in_progress_tickets,
            'today_bookings': today_bookings,
            'recent_tickets': recent_tickets,
            'recent_visitors': recent_visitors,
            'pinned_notices': pinned_notices,
            'active_poll': active_poll,
            'has_voted_active_poll': has_voted_active_poll,
            'active_sos_alerts': active_sos_alerts,
        })

    # --- RESIDENT VIEW ---
    elif user.role == 'RESIDENT':
        resident_flats = user.resident_flats.all() | user.owned_units.all()
        primary_flat = resident_flats.first()

        # Dues & Bills
        bills = MaintenanceBill.objects.filter(Q(resident=user) | Q(unit__in=resident_flats))
        unpaid_bills = bills.filter(status__in=[MaintenanceBill.Status.UNPAID, MaintenanceBill.Status.OVERDUE, MaintenanceBill.Status.PARTIAL])
        total_due_amount = sum(b.remaining_due for b in unpaid_bills)
        latest_bill = bills.order_by('-billing_month').first()

        # Passes, Tickets, Parcels
        active_passes = PreApprovedPass.objects.filter(host_resident=user, is_used=False, valid_until__gte=timezone.now())[:3]
        my_tickets = MaintenanceTicket.objects.filter(resident=user).order_by('-created_at')[:5]
        my_parcels = ParcelLog.objects.filter(unit__in=resident_flats, is_collected=False)
        my_amenity_bookings = AmenityBooking.objects.filter(resident=user, booking_date__gte=today, status=AmenityBooking.Status.CONFIRMED)[:3]
        my_vehicles = user.vehicles.filter(is_active=True)

        return render(request, 'dashboard/resident_dashboard.html', {
            'primary_flat': primary_flat,
            'resident_flats': resident_flats,
            'unpaid_bills': unpaid_bills,
            'total_due_amount': total_due_amount,
            'latest_bill': latest_bill,
            'active_passes': active_passes,
            'my_tickets': my_tickets,
            'my_parcels': my_parcels,
            'my_amenity_bookings': my_amenity_bookings,
            'my_vehicles': my_vehicles,
            'pinned_notices': pinned_notices,
            'active_poll': active_poll,
            'has_voted_active_poll': has_voted_active_poll,
            'active_sos_alerts': active_sos_alerts,
        })

    # --- STAFF VIEW ---
    elif user.role == 'STAFF':
        assigned_tickets = MaintenanceTicket.objects.filter(assigned_staff=user).order_by('-created_at')
        unassigned_tickets = MaintenanceTicket.objects.filter(assigned_staff__isnull=True, status=MaintenanceTicket.Status.OPEN)

        return render(request, 'dashboard/staff_dashboard.html', {
            'assigned_tickets': assigned_tickets,
            'unassigned_tickets': unassigned_tickets,
            'pinned_notices': pinned_notices,
            'active_sos_alerts': active_sos_alerts,
        })

    return redirect('accounts:login')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import json

from apps.properties.models import Unit, Wing, Vehicle, DomesticStaff, ResidentUnitMapping, MoveInOutRequest, RuleViolationReport
from apps.accounts.models import StaffProfile
from apps.billing.models import MaintenanceBill, BillPayment, SocietyExpense
from apps.gatekeeper.models import VisitorLog, PreApprovedPass, ParcelLog, SOSAlert
from apps.helpdesk.models import MaintenanceTicket
from apps.amenities.models import Amenity, AmenityBooking, EVChargingStation, EVChargingSession
from apps.communications.models import Notice, SocietyPoll, PollVote

def landing_page_view(request):
    """Public luxury building website showcasing Emerald Greens residences, amenities & smart society portal."""
    total_flats = Unit.objects.count()
    occupied_flats = Unit.objects.exclude(occupancy_status=Unit.OccupancyStatus.VACANT).count()
    wings_count = Wing.objects.count()
    active_amenities = list(Amenity.objects.filter(is_active=True))
    ev_chargers_count = EVChargingStation.objects.filter(is_active=True).count()
    pinned_notices = list(Notice.objects.filter(is_pinned=True, is_active=True).order_by('-created_at')[:3])
    
    today = timezone.now().date()
    active_poll = SocietyPoll.objects.filter(is_active=True, end_date__gte=today).first()

    return render(request, 'landing.html', {
        'total_flats': total_flats,
        'occupied_flats': occupied_flats,
        'wings_count': wings_count,
        'active_amenities': active_amenities,
        'ev_chargers_count': ev_chargers_count,
        'pinned_notices': pinned_notices,
        'active_poll': active_poll,
    })


@login_required
def dashboard_view(request):
    """Role-aware intelligent society management dashboard fully synchronized with the database."""
    user = request.user
    today = timezone.now().date()

    # Route guard directly to gate terminal if desired, or show guard view
    if user.role == 'GUARD':
        return redirect('gatekeeper:terminal')

    # Common metrics across roles
    pinned_notices = Notice.objects.filter(is_pinned=True, is_active=True)[:3]
    active_poll = SocietyPoll.objects.filter(is_active=True, end_date__gte=today).first()
    has_voted_active_poll = active_poll.user_has_voted(user) if active_poll else False
    active_sos_alerts = SOSAlert.objects.filter(is_resolved=False)[:3]

    # --- ADMIN & COMMITTEE VIEW ---
    if user.is_society_admin or user.is_committee_member:
        # 1. Exact Dynamic Occupancy Breakdown
        total_units = Unit.objects.count()
        owner_occupied_units = Unit.objects.filter(occupancy_status=Unit.OccupancyStatus.OWNER).count()
        rented_units = Unit.objects.filter(occupancy_status=Unit.OccupancyStatus.TENANT).count()
        occupied_units = owner_occupied_units + rented_units
        vacant_units = Unit.objects.filter(occupancy_status=Unit.OccupancyStatus.VACANT).count()
        occupancy_rate = round((occupied_units / total_units * 100) if total_units > 0 else 0, 1)

        # 2. Total Monthly Collections (Maintenance + Amenities + EV for current month)
        cur_year = today.year
        cur_month = today.month

        monthly_maint_collected = BillPayment.objects.filter(
            payment_status=BillPayment.PaymentStatus.SUCCESS,
            payment_date__year=cur_year,
            payment_date__month=cur_month
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0.00')

        monthly_amenity_collected = AmenityBooking.objects.filter(
            status=AmenityBooking.Status.CONFIRMED,
            booking_date__year=cur_year,
            booking_date__month=cur_month
        ).aggregate(t=Sum('total_fee'))['t'] or Decimal('0.00')

        monthly_ev_collected = EVChargingSession.objects.filter(
            status__in=[EVChargingSession.SessionStatus.COMPLETED, EVChargingSession.SessionStatus.ACTIVE],
            booking_date__year=cur_year,
            booking_date__month=cur_month
        ).aggregate(t=Sum('total_cost'))['t'] or Decimal('0.00')

        total_revenue = round(monthly_maint_collected + monthly_amenity_collected + monthly_ev_collected, 2)
        total_monthly_collections = total_revenue

        # Current month billing stats
        first_of_month = date(today.year, today.month, 1)
        month_bills = MaintenanceBill.objects.filter(billing_month=first_of_month)
        monthly_billed = month_bills.aggregate(t=Sum('total_amount'))['t'] or Decimal('0.00')
        monthly_collected = month_bills.aggregate(t=Sum('paid_amount'))['t'] or Decimal('0.00')
        monthly_pending = monthly_billed - monthly_collected
        collection_percentage = round((monthly_collected / monthly_billed * 100) if monthly_billed > 0 else 0, 1)

        # 3. Unpaid Dues / Arrears (Actual outstanding balance across all non-settled invoices)
        all_unpaid_bills = MaintenanceBill.objects.exclude(status=MaintenanceBill.Status.PAID)
        outstanding_dues = round(sum(Decimal(str(b.remaining_due)) for b in all_unpaid_bills), 2)

        # 4. Overdue Flat Invoices (Genuine past-due count: due_date < today and not fully paid)
        overdue_bills_count = all_unpaid_bills.filter(due_date__lt=today).count()
        unpaid_bills_count = all_unpaid_bills.count()

        # 5. Helpdesk Open Queue (Active open + in-progress tickets)
        open_tickets = MaintenanceTicket.objects.filter(status=MaintenanceTicket.Status.OPEN).count()
        in_progress_tickets = MaintenanceTicket.objects.filter(status=MaintenanceTicket.Status.IN_PROGRESS).count()
        pending_tickets = open_tickets + in_progress_tickets

        # 6. Total Society Reserves (All-time Income minus All-time Approved Expenses)
        all_time_maint_income = BillPayment.objects.filter(payment_status=BillPayment.PaymentStatus.SUCCESS).aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
        all_time_amenity_income = AmenityBooking.objects.filter(status=AmenityBooking.Status.CONFIRMED).aggregate(t=Sum('total_fee'))['t'] or Decimal('0.00')
        all_time_ev_income = EVChargingSession.objects.filter(status__in=[EVChargingSession.SessionStatus.COMPLETED, EVChargingSession.SessionStatus.ACTIVE]).aggregate(t=Sum('total_cost'))['t'] or Decimal('0.00')
        total_income = all_time_maint_income + all_time_amenity_income + all_time_ev_income
        total_expense = SocietyExpense.objects.filter(is_approved=True).aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
        net_reserve = round(total_income - total_expense, 2)

        # 7. Gate & Helpdesk live metrics
        inside_visitors_count = VisitorLog.objects.filter(status=VisitorLog.Status.INSIDE).count()
        active_visitors_count = inside_visitors_count
        today_bookings = AmenityBooking.objects.filter(booking_date=today, status=AmenityBooking.Status.CONFIRMED).count()

        recent_tickets = MaintenanceTicket.objects.select_related('unit', 'resident').order_by('-created_at')[:5]
        recent_visitors = VisitorLog.objects.select_related('unit').order_by('-entry_time')[:5]
        owner_occupied_units = Unit.objects.filter(occupancy_status=Unit.OccupancyStatus.OWNER).count()
        tenant_occupied_units = Unit.objects.filter(occupancy_status=Unit.OccupancyStatus.TENANT).count()

        # 8. Dynamic 6-Month Fiscal Cashflow Trend (Revenue vs Expenses)
        cashflow_labels = []
        cashflow_revenue = []
        cashflow_expenses = []

        for i in range(5, -1, -1):
            m_num = today.month - i
            y_num = today.year
            while m_num <= 0:
                m_num += 12
                y_num -= 1
            
            m_start = date(y_num, m_num, 1)
            m_label = m_start.strftime('%b %Y') if y_num != today.year else m_start.strftime('%b')
            cashflow_labels.append(m_label)

            # Revenue in this month: Maintenance payments + Amenity bookings + EV Charging
            rev_m = BillPayment.objects.filter(
                payment_status=BillPayment.PaymentStatus.SUCCESS,
                payment_date__year=y_num,
                payment_date__month=m_num
            ).aggregate(t=Sum('amount'))['t'] or Decimal('0.00')

            rev_a = AmenityBooking.objects.filter(
                status=AmenityBooking.Status.CONFIRMED,
                booking_date__year=y_num,
                booking_date__month=m_num
            ).aggregate(t=Sum('total_fee'))['t'] or Decimal('0.00')

            rev_e = EVChargingSession.objects.filter(
                status__in=[EVChargingSession.SessionStatus.COMPLETED, EVChargingSession.SessionStatus.ACTIVE],
                booking_date__year=y_num,
                booking_date__month=m_num
            ).aggregate(t=Sum('total_cost'))['t'] or Decimal('0.00')

            cashflow_revenue.append(float(round(rev_m + rev_a + rev_e, 2)))

            # Approved society expenses in this month
            exp_m = SocietyExpense.objects.filter(
                is_approved=True,
                expense_date__year=y_num,
                expense_date__month=m_num
            ).aggregate(t=Sum('amount'))['t'] or Decimal('0.00')

            cashflow_expenses.append(float(round(exp_m, 2)))

        # Common management data payload
        mgmt_context = {
            'total_units': total_units,
            'occupied_units': occupied_units,
            'owner_occupied_units': owner_occupied_units,
            'rented_units': rented_units,
            'tenant_occupied_units': rented_units,
            'vacant_units': vacant_units,
            'occupancy_rate': occupancy_rate,
            
            'total_revenue': total_revenue,
            'total_monthly_collections': total_monthly_collections,
            'monthly_maintenance_collected': monthly_maint_collected,
            'monthly_amenity_collected': monthly_amenity_collected,
            'monthly_ev_collected': monthly_ev_collected,
            
            'outstanding_dues': outstanding_dues,
            'overdue_bills_count': overdue_bills_count,
            'unpaid_bills_count': unpaid_bills_count,
            
            'monthly_billed': monthly_billed,
            'monthly_collected': monthly_collected,
            'monthly_pending': monthly_pending,
            'collection_percentage': collection_percentage,
            'net_reserve': net_reserve,
            'monthly_pending': monthly_pending,
            'collection_percentage': collection_percentage,
            'net_reserve': net_reserve,
            'total_revenue': monthly_collected,
            'outstanding_dues': monthly_pending,
            'unpaid_bills_count': month_bills.filter(status__in=[MaintenanceBill.Status.UNPAID, MaintenanceBill.Status.OVERDUE, MaintenanceBill.Status.PARTIAL]).count(),
            'pending_tickets': pending_tickets,
            'owner_occupied_units': owner_occupied_units,
            'tenant_occupied_units': tenant_occupied_units,
            'inside_visitors_count': active_visitors_count,
            'active_visitors_count': active_visitors_count,
            'open_tickets': open_tickets,
            'in_progress_tickets': in_progress_tickets,

            'open_tickets': open_tickets,
            'in_progress_tickets': in_progress_tickets,
            
            'inside_visitors_count': inside_visitors_count,
            'active_visitors_count': active_visitors_count,
            'today_bookings': today_bookings,
            'recent_tickets': recent_tickets,
            'recent_visitors': recent_visitors,
            
            'cashflow_labels': cashflow_labels,
            'cashflow_revenue': cashflow_revenue,
            'cashflow_expenses': cashflow_expenses,
            'cashflow_labels_json': json.dumps(cashflow_labels),
            'cashflow_revenue_json': json.dumps(cashflow_revenue),
            'cashflow_expenses_json': json.dumps(cashflow_expenses),
            
            'pinned_notices': pinned_notices,
            'active_poll': active_poll,
            'has_voted_active_poll': has_voted_active_poll,
            'active_sos_alerts': active_sos_alerts,
        }

        # 1. Hon. Secretary Dashboard
        if user.role == 'SECRETARY':
            total_residents = ResidentUnitMapping.objects.filter(is_active=True).count()
            pending_move_requests = MoveInOutRequest.objects.filter(status=MoveInOutRequest.Status.PENDING).select_related('unit', 'resident')
            active_violations = RuleViolationReport.objects.filter(is_resolved=False).select_related('unit')[:5]
            recent_units = Unit.objects.select_related('wing', 'owner', 'primary_resident').order_by('wing__code', 'unit_number')[:10]
            recent_notices = Notice.objects.all().order_by('-published_date')[:5]

            sec_context = dict(mgmt_context)
            sec_context.update({
                'total_residents': total_residents,
                'pending_move_requests': pending_move_requests,
                'active_violations': active_violations,
                'recent_units': recent_units,
                'recent_notices': recent_notices,
                'open_tickets_count': pending_tickets,
            })
            return render(request, 'dashboard/secretary_dashboard.html', sec_context)

        # 2. Hon. Treasurer & Accountant Dashboard
        elif user.role in ['TREASURER', 'ACCOUNTANT']:
            recent_payments = BillPayment.objects.select_related('bill', 'bill__unit').order_by('-payment_date')[:10]
            overdue_bills = MaintenanceBill.objects.filter(due_date__lt=today).exclude(status=MaintenanceBill.Status.PAID).select_related('unit', 'resident').order_by('due_date')[:10]
            society_expenses = SocietyExpense.objects.all().order_by('-expense_date')[:10]

            treas_context = dict(mgmt_context)
            treas_context.update({
                'recent_payments': recent_payments,
                'overdue_bills': overdue_bills,
                'society_expenses': society_expenses,
            })
            return render(request, 'dashboard/treasurer_dashboard.html', treas_context)

        # 3. Facility Manager Dashboard
        elif user.role == 'FACILITY_MGR':
            today_bookings_list = AmenityBooking.objects.filter(booking_date=today, status=AmenityBooking.Status.CONFIRMED).select_related('amenity', 'resident')
            ev_stations = EVChargingStation.objects.all()
            active_ev_sessions = EVChargingSession.objects.filter(status=EVChargingSession.SessionStatus.ACTIVE).select_related('station', 'user')
            unassigned_tickets = MaintenanceTicket.objects.filter(assigned_staff__isnull=True).exclude(status=MaintenanceTicket.Status.RESOLVED).select_related('unit', 'resident')
            duty_staff = StaffProfile.objects.filter(is_on_duty=True).select_related('user')
            pending_moves = MoveInOutRequest.objects.filter(status=MoveInOutRequest.Status.PENDING).select_related('unit', 'resident')

            fac_context = dict(mgmt_context)
            fac_context.update({
                'today_bookings': today_bookings_list,
                'ev_stations': ev_stations,
                'active_ev_sessions': active_ev_sessions,
                'unassigned_tickets': unassigned_tickets,
                'duty_staff': duty_staff,
                'pending_moves': pending_moves,
            })
            return render(request, 'dashboard/facility_dashboard.html', fac_context)

        # 4. Super Admin / President & Committee Dashboard
        return render(request, 'dashboard/admin_dashboard.html', mgmt_context)

    # --- TENANT VIEW ---
    elif user.role == 'TENANT':
        tenant_flats = (user.resident_flats.all() | Unit.objects.filter(primary_resident=user)).distinct()
        primary_flat = tenant_flats.first()

        bills = MaintenanceBill.objects.filter(
            Q(resident=user) | Q(unit__in=tenant_flats)
        ).select_related('unit', 'resident').order_by('-billing_month').distinct()

        my_unpaid_bills = bills.filter(status__in=[MaintenanceBill.Status.UNPAID, MaintenanceBill.Status.OVERDUE, MaintenanceBill.Status.PARTIAL])
        total_due_amount = round(sum(Decimal(str(b.remaining_due)) for b in my_unpaid_bills), 2)
        latest_bill = bills.first()

        active_passes = PreApprovedPass.objects.filter(host_resident=user, is_used=False, valid_until__gte=timezone.now())[:5]
        all_my_tickets = MaintenanceTicket.objects.filter(resident=user).order_by('-created_at')
        my_tickets = all_my_tickets[:5]
        open_tickets = all_my_tickets.filter(status__in=[MaintenanceTicket.Status.OPEN, MaintenanceTicket.Status.IN_PROGRESS])
        my_parcels = ParcelLog.objects.filter(unit__in=tenant_flats, is_collected=False)
        my_amenity_bookings = AmenityBooking.objects.filter(resident=user, booking_date__gte=today, status=AmenityBooking.Status.CONFIRMED)[:5]
        my_vehicles = user.vehicles.filter(is_active=True)

        return render(request, 'dashboard/tenant_dashboard.html', {
            'primary_flat': primary_flat,
            'primary_unit': primary_flat,
            'resident_flats': tenant_flats,
            'my_bills': bills,
            'my_unpaid_bills': my_unpaid_bills,
            'unpaid_bills': my_unpaid_bills,
            'total_due_amount': total_due_amount,
            'total_unpaid_amount': total_due_amount,
            'latest_bill': latest_bill,
            'active_passes': active_passes,
            'my_tickets': my_tickets,
            'open_tickets': open_tickets,
            'my_parcels': my_parcels,
            'uncollected_parcels': my_parcels,
            'my_amenity_bookings': my_amenity_bookings,
            'my_vehicles': my_vehicles,
            'pinned_notices': pinned_notices,
            'active_poll': active_poll,
            'has_voted_active_poll': has_voted_active_poll,
            'active_sos_alerts': active_sos_alerts,
        })

    # --- OWNER / RESIDENT VIEW ---
    elif user.role in ['OWNER', 'RESIDENT'] or user.is_flat_owner:
        resident_flats = (user.resident_flats.all() | user.owned_units.all()).distinct()
        primary_flat = resident_flats.first()

        # Dues & Bills
        bills = MaintenanceBill.objects.filter(
            Q(resident=user) | Q(unit__in=resident_flats)
        ).select_related('unit', 'resident').order_by('-billing_month').distinct()
        
        my_unpaid_bills = bills.filter(status__in=[MaintenanceBill.Status.UNPAID, MaintenanceBill.Status.OVERDUE, MaintenanceBill.Status.PARTIAL])
        total_due_amount = round(sum(Decimal(str(b.remaining_due)) for b in my_unpaid_bills), 2)
        latest_bill = bills.first()

        # Passes, Tickets, Parcels
        active_passes = PreApprovedPass.objects.filter(host_resident=user, is_used=False, valid_until__gte=timezone.now())[:5]
        all_my_tickets = MaintenanceTicket.objects.filter(resident=user).order_by('-created_at')
        my_tickets = all_my_tickets[:5]
        open_tickets = all_my_tickets.filter(status__in=[MaintenanceTicket.Status.OPEN, MaintenanceTicket.Status.IN_PROGRESS])

        my_parcels = ParcelLog.objects.filter(unit__in=resident_flats, is_collected=False)
        my_amenity_bookings = AmenityBooking.objects.filter(resident=user, booking_date__gte=today, status=AmenityBooking.Status.CONFIRMED)[:5]
        my_vehicles = user.vehicles.filter(is_active=True)

        return render(request, 'dashboard/resident_dashboard.html', {
            'primary_flat': primary_flat,
            'primary_unit': primary_flat,
            'resident_flats': resident_flats,
            'my_bills': bills,
            'my_unpaid_bills': my_unpaid_bills,
            'unpaid_bills': my_unpaid_bills,
            'total_due_amount': total_due_amount,
            'total_unpaid_amount': total_due_amount,
            'latest_bill': latest_bill,
            'my_bills': bills,
            'my_unpaid_bills': unpaid_bills,
            'active_passes': active_passes,
            'my_tickets': my_tickets,
            'my_unpaid_bills': unpaid_bills,
            'active_passes': active_passes,
            'my_tickets': my_tickets,
            'open_tickets': open_tickets,
            'my_parcels': my_parcels,
            'uncollected_parcels': my_parcels,
            'my_amenity_bookings': my_amenity_bookings,

            'my_parcels': my_parcels,
            'uncollected_parcels': my_parcels,
            'my_amenity_bookings': my_amenity_bookings,
            'my_vehicles': my_vehicles,
            'pinned_notices': pinned_notices,
            'active_poll': active_poll,
            'has_voted_active_poll': has_voted_active_poll,
            'active_sos_alerts': active_sos_alerts,
        })

    # --- STAFF VIEW ---
    elif user.role == 'STAFF':
        assigned_tickets = MaintenanceTicket.objects.filter(assigned_staff=user).select_related('unit', 'resident').order_by('-created_at')
        unassigned_tickets = MaintenanceTicket.objects.filter(assigned_staff__isnull=True, status=MaintenanceTicket.Status.OPEN).select_related('unit', 'resident')

        return render(request, 'dashboard/staff_dashboard.html', {
            'assigned_tickets': assigned_tickets,
            'unassigned_tickets': unassigned_tickets,
            'pinned_notices': pinned_notices,
            'active_sos_alerts': active_sos_alerts,
        })

    # Superuser fallback or default
    if user.is_superuser or user.is_staff:
        return redirect('dashboard')
    
    return redirect('accounts:login')


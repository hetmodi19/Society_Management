from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import random

from .models import VisitorLog, PreApprovedPass, ParcelLog, SOSAlert
from .forms import VisitorEntryForm, PreApprovedPassForm, ParcelLogForm, SOSAlertForm
from apps.properties.models import Unit, DomesticStaff
from apps.accounts.decorators import guard_required

@guard_required
def terminal_view(request):
    """Live Gatekeeper Terminal for Security Guards."""
    inside_visitors = VisitorLog.objects.filter(status=VisitorLog.Status.INSIDE).select_related('unit', 'host_resident')
    recent_entries = VisitorLog.objects.select_related('unit', 'host_resident').order_by('-entry_time')[:15]
    uncollected_parcels = ParcelLog.objects.filter(is_collected=False).select_related('unit')
    active_alerts = SOSAlert.objects.filter(is_resolved=False).select_related('triggered_by', 'unit')

    entry_form = VisitorEntryForm()
    parcel_form = ParcelLogForm()

    return render(request, 'gatekeeper/terminal.html', {
        'inside_visitors': inside_visitors,
        'recent_entries': recent_entries,
        'uncollected_parcels': uncollected_parcels,
        'active_alerts': active_alerts,
        'entry_form': entry_form,
        'parcel_form': parcel_form,
    })


@guard_required
def visitor_entry_view(request):
    """Guard logs a walk-in visitor entry."""
    if request.method == 'POST':
        form = VisitorEntryForm(request.POST)
        if form.is_valid():
            visitor = form.save(commit=False)
            visitor.entry_guard = request.user
            visitor.status = VisitorLog.Status.INSIDE
            visitor.save()
            messages.success(request, f"Entry cleared for {visitor.visitor_name} to Flat {visitor.unit.unit_number}.")
        else:
            messages.error(request, "Failed to log entry. Please check form values.")
    return redirect('gatekeeper:terminal')


@guard_required
def visitor_checkout_view(request, pk):
    """Mark visitor as departed."""
    visitor = get_object_or_404(VisitorLog, pk=pk)
    visitor.status = VisitorLog.Status.CHECKED_OUT
    visitor.exit_time = timezone.now()
    visitor.save()
    messages.info(request, f"Visitor {visitor.visitor_name} checked out.")
    return redirect('gatekeeper:terminal')


@guard_required
def verify_pass_view(request):
    """Verify 6-digit visitor pass or 4-digit helper passcode at security desk."""
    passcode = request.POST.get('passcode', '').strip().upper()

    if not passcode:
        messages.error(request, "Please enter a passcode or PIN.")
        return redirect('gatekeeper:terminal')

    # Check 6-digit pre-approved guest pass
    pre_pass = PreApprovedPass.objects.filter(pass_code=passcode).first()
    if pre_pass:
        if pre_pass.is_used:
            messages.warning(request, f"Pass {passcode} has ALREADY been used.")
        elif timezone.now() > pre_pass.valid_until:
            messages.error(request, f"Pass {passcode} EXPIRED on {pre_pass.valid_until.strftime('%d %b %H:%M')}.")
        else:
            pre_pass.is_used = True
            pre_pass.used_at = timezone.now()
            pre_pass.save()

            VisitorLog.objects.create(
                visitor_name=pre_pass.visitor_name,
                phone_number=pre_pass.visitor_phone,
                unit=pre_pass.unit,
                host_resident=pre_pass.host_resident,
                visitor_type=VisitorLog.VisitorType.GUEST,
                purpose=f"Pre-approved: {pre_pass.purpose}",
                is_pre_approved=True,
                status=VisitorLog.Status.INSIDE,
                entry_guard=request.user
            )
            messages.success(request, f"VERIFIED: Welcome {pre_pass.visitor_name}! Clearance granted for Flat {pre_pass.unit.unit_number}.")
            return redirect('gatekeeper:terminal')

    # Check 4-digit daily helper passcode
    helper = DomesticStaff.objects.filter(passcode=passcode, is_active=True).first()
    if helper:
        assigned_flat = helper.assigned_units.first()
        VisitorLog.objects.create(
            visitor_name=f"{helper.name} ({helper.get_role_type_display()})",
            phone_number=helper.phone_number,
            unit=assigned_flat or Unit.objects.first(),
            visitor_type=VisitorLog.VisitorType.SERVICE,
            purpose=f"Daily Helper Check-In: {helper.get_role_type_display()}",
            status=VisitorLog.Status.INSIDE,
            entry_guard=request.user
        )
        messages.success(request, f"CLEARED: Helper {helper.name} ({helper.get_role_type_display()}) checked in.")
        return redirect('gatekeeper:terminal')

    messages.error(request, f"INVALID PASSCODE '{passcode}'. No matching active pass found.")
    return redirect('gatekeeper:terminal')


@login_required
def passes_view(request):
    """View generated visitor passes. Standard residents only view passes for their flats."""
    if request.user.is_society_admin or request.user.is_security_guard:
        passes = PreApprovedPass.objects.select_related('unit', 'host_resident').all()
    else:
        passes = PreApprovedPass.objects.filter(
            Q(host_resident=request.user) |
            Q(unit__owner=request.user) |
            Q(unit__primary_resident=request.user)
        ).select_related('unit', 'host_resident').distinct()

    return render(request, 'gatekeeper/passes.html', {'passes': passes})


@login_required
def create_pass_view(request):
    """Generate a 6-digit OTP guest pass."""
    user_flats = (request.user.resident_flats.all() | request.user.owned_units.all()).distinct()
    if request.user.is_society_admin:
        user_flats = Unit.objects.all()

    if request.method == 'POST':
        form = PreApprovedPassForm(request.POST)
        if form.is_valid():
            pass_obj = form.save(commit=False)
            pass_obj.host_resident = request.user
            
            # Security verification
            if not (request.user.is_society_admin or pass_obj.unit in user_flats):
                messages.error(request, "You can only generate passes for your assigned unit.")
                return redirect('gatekeeper:passes')

            # Generate unique 6-digit PIN
            pass_obj.pass_code = str(random.randint(100000, 999999))
            pass_obj.valid_until = timezone.now() + timedelta(hours=int(request.POST.get('validity_hours', 12)))
            pass_obj.save()

            messages.success(request, f"Guest Pass created! Passcode: {pass_obj.pass_code}")
            return redirect('gatekeeper:passes')
    else:
        form = PreApprovedPassForm()
        form.fields['unit'].queryset = user_flats

    return render(request, 'gatekeeper/create_pass.html', {'form': form})


@guard_required
def parcel_desk_view(request):
    """Manage parcel delivery lockers."""
    if request.method == 'POST':
        form = ParcelLogForm(request.POST)
        if form.is_valid():
            parcel = form.save(commit=False)
            parcel.guard = request.user
            parcel.save()
            messages.success(request, f"Parcel for Flat {parcel.unit.unit_number} logged in locker.")
            return redirect('gatekeeper:parcels')
    else:
        form = ParcelLogForm()

    parcels = ParcelLog.objects.select_related('unit', 'guard').order_by('-received_at')[:30]
    return render(request, 'gatekeeper/parcel_desk.html', {'form': form, 'parcels': parcels})


@guard_required
def collect_parcel_view(request, pk):
    """Mark parcel collected by resident."""
    parcel = get_object_or_404(ParcelLog, pk=pk)
    parcel.is_collected = True
    parcel.collected_at = timezone.now()
    parcel.save()
    messages.success(request, f"Parcel for Flat {parcel.unit.unit_number} marked collected.")
    return redirect('gatekeeper:parcels')


@login_required
def trigger_sos_view(request):
    """Trigger emergency panic broadcast."""
    user_flats = (request.user.resident_flats.all() | request.user.owned_units.all()).distinct()
    default_flat = user_flats.first()

    if request.method == 'POST':
        form = SOSAlertForm(request.POST)
        if form.is_valid():
            sos = form.save(commit=False)
            sos.triggered_by = request.user
            if default_flat and not sos.unit:
                sos.unit = default_flat
            sos.save()
            messages.error(request, f"🚨 EMERGENCY ALARM BROADCASTED: {sos.get_alert_type_display()}!")
            return redirect('dashboard')
    else:
        form = SOSAlertForm(initial={'unit': default_flat})

    return render(request, 'gatekeeper/trigger_sos.html', {'form': form})


@login_required
def resolve_sos_view(request, pk):
    """Mark an emergency alarm resolved."""
    if not (request.user.is_society_admin or request.user.is_security_guard or request.user.is_committee_member):
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    alert = get_object_or_404(SOSAlert, pk=pk)
    alert.is_resolved = True
    alert.resolved_at = timezone.now()
    alert.resolved_by = request.user
    alert.save()
    messages.success(request, f"Emergency Alert #{alert.id} marked resolved.")
    return redirect('dashboard')


gate_terminal_view = terminal_view
verify_passcode_view = verify_pass_view

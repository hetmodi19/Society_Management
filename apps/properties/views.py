from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import Wing, Unit, ResidentUnitMapping, Vehicle, DomesticStaff, MoveInOutRequest, RuleViolationReport
from .forms import UnitForm, VehicleForm, DomesticStaffForm, MoveInOutRequestForm, RuleViolationReportForm
from apps.accounts.decorators import committee_required

@login_required
def unit_list_view(request):
    """View flats/units. Admins/Committee view all flats; Residents view their owned or leased units."""
    wing_id = request.GET.get('wing')
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')

    wings = Wing.objects.annotate(total_flats=Count('units'))
    
    if request.user.is_society_admin or request.user.is_committee_member or request.user.is_security_guard:
        units = Unit.objects.select_related('wing', 'owner', 'primary_resident').prefetch_related('vehicles', 'resident_mappings')
    else:
        # Standard Resident: strictly isolate to their owned or leased units
        units = Unit.objects.filter(
            Q(owner=request.user) | Q(primary_resident=request.user)
        ).select_related('wing', 'owner', 'primary_resident').prefetch_related('vehicles', 'resident_mappings').distinct()

    if wing_id:
        units = units.filter(wing_id=wing_id)
    if status_filter:
        units = units.filter(occupancy_status=status_filter)
    if search_query:
        units = units.filter(
            Q(unit_number__icontains=search_query) |
            Q(primary_resident__first_name__icontains=search_query) |
            Q(primary_resident__last_name__icontains=search_query) |
            Q(owner__first_name__icontains=search_query) |
            Q(owner__last_name__icontains=search_query)
        )

    total_units_count = Unit.objects.count()
    occupied_count = Unit.objects.exclude(occupancy_status=Unit.OccupancyStatus.VACANT).count()
    vacant_count = Unit.objects.filter(occupancy_status=Unit.OccupancyStatus.VACANT).count()
    occupancy_rate = round((occupied_count / total_units_count * 100) if total_units_count > 0 else 0, 1)

    return render(request, 'properties/unit_list.html', {
        'units': units,
        'wings': wings,
        'selected_wing': wing_id,
        'search_query': search_query,
        'selected_status': status_filter,
        'total_units_count': total_units_count,
        'occupied_count': occupied_count,
        'vacant_count': vacant_count,
        'occupancy_rate': occupancy_rate,
    })


@login_required
def unit_detail_view(request, pk):
    """Detailed profile of a flat/unit with strict data privacy for Owner, Tenant, and Committee."""
    unit = get_object_or_404(Unit.objects.select_related('wing', 'owner', 'primary_resident'), pk=pk)

    # Strict Privacy Check: Only Flat Owner, Flat Tenant, or Committee/Admin can view private flat data
    is_owner = (unit.owner == request.user)
    is_tenant = (unit.primary_resident == request.user and unit.occupancy_status == Unit.OccupancyStatus.TENANT)
    is_management = (request.user.is_society_admin or request.user.is_committee_member or request.user.is_security_guard)

    if not (is_owner or is_tenant or is_management):
        messages.error(request, f"Access Denied: You do not have permission to view private records for Flat {unit.unit_number}.")
        return redirect('properties:units')

    mappings = unit.resident_mappings.filter(is_active=True).select_related('user')
    vehicles = unit.vehicles.filter(is_active=True)
    staff = unit.domestic_staff_members.filter(is_active=True)
    
    # Financial & Helpdesk isolation
    if is_owner or is_management:
        recent_bills = unit.maintenance_bills.order_by('-billing_month')[:5]
    elif is_tenant:
        recent_bills = unit.maintenance_bills.filter(resident=request.user).order_by('-billing_month')[:5]
    else:
        recent_bills = []

    recent_tickets = unit.maintenance_tickets.order_by('-created_at')[:5]

    return render(request, 'properties/unit_detail.html', {
        'unit': unit,
        'is_owner': is_owner,
        'is_tenant': is_tenant,
        'mappings': mappings,
        'vehicles': vehicles,
        'staff': staff,
        'recent_bills': recent_bills,
        'recent_tickets': recent_tickets,
    })


@login_required
def resident_directory_view(request):
    """Searchable resident phonebook & directory (public contact directory)."""
    search_query = request.GET.get('q', '').strip()
    wing_code = request.GET.get('wing', '')

    wings = Wing.objects.all()
    units = Unit.objects.select_related('wing', 'primary_resident', 'owner').exclude(occupancy_status=Unit.OccupancyStatus.VACANT)

    if wing_code:
        units = units.filter(wing__code=wing_code)
    if search_query:
        units = units.filter(
            Q(unit_number__icontains=search_query) |
            Q(primary_resident__first_name__icontains=search_query) |
            Q(primary_resident__last_name__icontains=search_query) |
            Q(primary_resident__phone_number__icontains=search_query)
        )

    return render(request, 'properties/resident_directory.html', {
        'units': units,
        'wings': wings,
        'search_query': search_query,
        'selected_wing': wing_code,
    })


@login_required
def vehicle_list_view(request):
    """Vehicle management & parking slot directory."""
    search_query = request.GET.get('q', '').strip()
    vehicles = Vehicle.objects.select_related('owner', 'unit', 'unit__wing').filter(is_active=True)

    if not (request.user.is_society_admin or request.user.is_committee_member or request.user.is_security_guard):
        vehicles = vehicles.filter(owner=request.user)

    if search_query:
        vehicles = vehicles.filter(
            Q(license_plate__icontains=search_query) |
            Q(make_model__icontains=search_query) |
            Q(unit__unit_number__icontains=search_query) |
            Q(parking_slot__icontains=search_query)
        )

    return render(request, 'properties/vehicle_list.html', {
        'vehicles': vehicles,
        'search_query': search_query,
    })


@login_required
def add_vehicle_view(request):
    """Register a new vehicle."""
    user_flats = (request.user.resident_flats.all() | request.user.owned_units.all()).distinct()
    if request.user.is_society_admin or request.user.is_committee_member:
        user_flats = Unit.objects.all()

    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            # Ensure user owns or leases the selected unit
            if not (request.user.is_society_admin or vehicle.unit in user_flats):
                messages.error(request, "Invalid flat selection.")
                return redirect('properties:vehicles')

            vehicle.save()
            messages.success(request, f"Vehicle {vehicle.license_plate} registered successfully!")
            return redirect('properties:vehicles')
    else:
        form = VehicleForm()
        form.fields['unit'].queryset = user_flats

    return render(request, 'properties/add_vehicle.html', {'form': form})


@login_required
def domestic_staff_list_view(request):
    """List helper staff badges & domestic staff directory."""
    staff_members = DomesticStaff.objects.prefetch_related('assigned_units').filter(is_active=True)
    search_query = request.GET.get('q', '').strip()

    if search_query:
        staff_members = staff_members.filter(
            Q(name__icontains=search_query) |
            Q(passcode__icontains=search_query) |
            Q(role_type__icontains=search_query)
        )

    return render(request, 'properties/domestic_staff_list.html', {
        'staff_members': staff_members,
        'search_query': search_query,
    })


@login_required
def add_domestic_staff_view(request):
    """Register a new domestic helper."""
    if not (request.user.is_society_admin or request.user.is_committee_member or request.user.is_resident_user):
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = DomesticStaffForm(request.POST)
        if form.is_valid():
            staff = form.save()
            messages.success(request, f"Daily Helper {staff.name} registered with Gate Passcode: {staff.passcode}")
            return redirect('properties:staff')
    else:
        form = DomesticStaffForm()

    return render(request, 'properties/add_domestic_staff.html', {'form': form})


@login_required
def move_requests_view(request):
    """Move-In / Move-Out & Service Lift Scheduling."""
    user_flats = (request.user.resident_flats.all() | request.user.owned_units.all()).distinct()
    if request.user.is_society_admin or request.user.is_committee_member:
        user_flats = Unit.objects.all()
        requests_list = MoveInOutRequest.objects.select_related('unit', 'resident').all()
    else:
        requests_list = MoveInOutRequest.objects.filter(resident=request.user).select_related('unit')

    if request.method == 'POST':
        form = MoveInOutRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.resident = request.user
            if not (request.user.is_society_admin or req.unit in user_flats):
                messages.error(request, "You can only request shifting for your own unit.")
                return redirect('properties:move_requests')

            req.save()
            messages.success(request, f"Move Request submitted for {req.move_date}! Security clearance initiated.")
            return redirect('properties:move_requests')
    else:
        form = MoveInOutRequestForm()
        form.fields['unit'].queryset = user_flats

    return render(request, 'properties/move_requests.html', {
        'requests_list': requests_list,
        'form': form,
    })


@login_required
def violations_view(request):
    """Report and track parking disputes, noise, and rule infractions."""
    user_flats = (request.user.resident_flats.all() | request.user.owned_units.all()).distinct()
    if request.user.is_society_admin or request.user.is_committee_member:
        violations_list = RuleViolationReport.objects.select_related('unit', 'reported_by').all()
    else:
        violations_list = RuleViolationReport.objects.filter(reported_by=request.user).select_related('unit')

    if request.method == 'POST':
        form = RuleViolationReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.reported_by = request.user
            report.save()
            messages.success(request, "Infraction report logged. Society management will review evidence.")
            return redirect('properties:violations')
    else:
        form = RuleViolationReportForm()

    return render(request, 'properties/violations.html', {
        'violations_list': violations_list,
        'form': form,
    })

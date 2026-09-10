from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import Wing, Unit, ResidentUnitMapping, Vehicle, DomesticStaff, MoveInOutRequest, RuleViolationReport
from .forms import UnitForm, VehicleForm, DomesticStaffForm, MoveInOutRequestForm, RuleViolationReportForm, ResidentForm, ResidentEditForm
from apps.accounts.models import User, ResidentProfile

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
    owner_occupied_count = Unit.objects.filter(occupancy_status=Unit.OccupancyStatus.OWNER).count()
    rented_count = Unit.objects.filter(occupancy_status=Unit.OccupancyStatus.TENANT).count()
    vacant_count = Unit.objects.filter(occupancy_status=Unit.OccupancyStatus.VACANT).count()
    occupied_count = owner_occupied_count + rented_count
    occupancy_rate = round((occupied_count / total_units_count * 100) if total_units_count > 0 else 0, 1)

    return render(request, 'properties/unit_list.html', {
        'units': units,
        'wings': wings,
        'selected_wing': wing_id,
        'search_query': search_query,
        'selected_status': status_filter,
        'total_units_count': total_units_count,
        'occupied_count': occupied_count,
        'owner_occupied_count': owner_occupied_count,
        'rented_count': rented_count,
        'vacant_count': vacant_count,
        'occupancy_rate': occupancy_rate,
    })


@login_required
def add_unit_view(request):
    """Add a new flat/unit to the society database."""
    if not (request.user.is_society_admin or request.user.is_committee_member):
        messages.error(request, "Permission Denied: Only Society Admins and Committee members can add new units.")
        return redirect('properties:units')

    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            messages.success(request, f"Flat {unit.unit_number} ({unit.wing.code}) created successfully!")
            return redirect('properties:unit_detail', pk=unit.pk)
    else:
        form = UnitForm()

    return render(request, 'properties/unit_form.html', {
        'form': form,
        'title': 'Add New Society Flat / Unit',
        'is_edit': False,
    })


@login_required
def edit_unit_view(request, pk):
    """Edit flat/unit details, occupancy status, and owner/tenant allocation."""
    unit = get_object_or_404(Unit, pk=pk)

    if not (request.user.is_society_admin or request.user.is_committee_member):
        messages.error(request, "Permission Denied: Only Society Admins and Committee members can edit unit details.")
        return redirect('properties:unit_detail', pk=unit.pk)

    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            saved_unit = form.save()
            messages.success(request, f"Flat {saved_unit.unit_number} details updated successfully!")
            return redirect('properties:unit_detail', pk=saved_unit.pk)
    else:
        form = UnitForm(instance=unit)

    return render(request, 'properties/unit_form.html', {
        'form': form,
        'unit': unit,
        'title': f"Edit Flat {unit.unit_number} Details",
        'is_edit': True,
    })


@login_required
def add_resident_view(request):
    """Register a new resident with authentic persona details and optional flat assignment."""
    if not (request.user.is_society_admin or request.user.is_committee_member):
        messages.error(request, "Permission Denied: Only Society Admins and Committee members can register new residents.")
        return redirect('properties:directory')

    if request.method == 'POST':
        form = ResidentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username'].strip().lower()
            if User.objects.filter(username=username).exists():
                messages.error(request, f"Username '{username}' already exists. Please choose a different username.")
                return render(request, 'properties/resident_form.html', {'form': form, 'title': 'Register New Resident', 'is_edit': False})

            user = User.objects.create_user(
                username=username,
                email=data['email'],
                password=data['password'] or 'resident123',
                first_name=data['first_name'],
                last_name=data['last_name'],
                role=User.Role.RESIDENT,
                phone_number=data['phone_number'],
            )

            res_type = data['resident_type']
            ResidentProfile.objects.create(
                user=user,
                resident_type=res_type,
                occupation=data.get('occupation', ''),
                emergency_contact_name=data.get('emergency_contact_name', ''),
                emergency_contact_phone=data.get('emergency_contact_phone', ''),
                blood_group=data.get('blood_group', 'Unknown'),
            )

            unit = data.get('unit')
            if unit:
                if res_type == 'OWNER':
                    unit.owner = user
                    unit.primary_resident = user
                    unit.occupancy_status = Unit.OccupancyStatus.OWNER
                    unit.save()
                    ResidentUnitMapping.objects.create(user=user, unit=unit, relation_type=ResidentUnitMapping.Relation.OWNER, is_primary=True)
                else:
                    unit.primary_resident = user
                    unit.occupancy_status = Unit.OccupancyStatus.TENANT
                    unit.save()
                    ResidentUnitMapping.objects.create(user=user, unit=unit, relation_type=ResidentUnitMapping.Relation.TENANT, is_primary=True)

            messages.success(request, f"Resident {user.full_name} registered successfully!")
            return redirect('properties:directory')
    else:
        initial_unit_id = request.GET.get('unit')
        initial_data = {}
        if initial_unit_id:
            try:
                initial_data['unit'] = Unit.objects.get(pk=initial_unit_id)
            except Unit.DoesNotExist:
                pass
        form = ResidentForm(initial=initial_data)

    return render(request, 'properties/resident_form.html', {
        'form': form,
        'title': 'Register New Resident',
        'is_edit': False,
    })


@login_required
def edit_resident_view(request, pk):
    """Edit resident profile, contact details, and flat mapping."""
    user = get_object_or_404(User, pk=pk)

    if not (request.user.is_society_admin or request.user.is_committee_member or request.user == user):
        messages.error(request, "Permission Denied: You cannot edit this resident's profile.")
        return redirect('properties:directory')

    profile, _ = ResidentProfile.objects.get_or_create(user=user)
    current_unit = user.resident_flats.first() or user.owned_units.first()

    if request.method == 'POST':
        form = ResidentEditForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.email = data['email']
            user.phone_number = data['phone_number']
            user.save()

            profile.resident_type = data['resident_type']
            profile.occupation = data.get('occupation', '')
            profile.emergency_contact_name = data.get('emergency_contact_name', '')
            profile.emergency_contact_phone = data.get('emergency_contact_phone', '')
            profile.blood_group = data.get('blood_group', 'Unknown')
            profile.save()

            new_unit = data.get('unit')
            if new_unit and new_unit != current_unit:
                if data['resident_type'] == 'OWNER':
                    new_unit.owner = user
                    new_unit.primary_resident = user
                    new_unit.occupancy_status = Unit.OccupancyStatus.OWNER
                else:
                    new_unit.primary_resident = user
                    new_unit.occupancy_status = Unit.OccupancyStatus.TENANT
                new_unit.save()

            messages.success(request, f"Resident {user.full_name}'s details updated successfully!")
            return redirect('properties:directory')
    else:
        form = ResidentEditForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.phone_number,
            'resident_type': profile.resident_type,
            'unit': current_unit,
            'occupation': profile.occupation,
            'emergency_contact_name': profile.emergency_contact_name,
            'emergency_contact_phone': profile.emergency_contact_phone,
            'blood_group': profile.blood_group,
        })

    return render(request, 'properties/resident_form.html', {
        'form': form,
        'user_obj': user,
        'title': f"Edit Details for {user.full_name}",
        'is_edit': True,
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
        'is_management': is_management,
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
            Q(primary_resident__phone_number__icontains=search_query) |
            Q(owner__first_name__icontains=search_query) |
            Q(owner__last_name__icontains=search_query)
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


@login_required
def delete_unit_view(request, pk):
    """Delete a flat/unit from society records (Admin/Committee only)."""
    unit = get_object_or_404(Unit, pk=pk)
    if not (request.user.is_society_admin or request.user.is_committee_member):
        messages.error(request, "Permission Denied: Only Society Admins and Committee members can delete units.")
        return redirect('properties:units')

    if request.method == 'POST':
        unit_num = unit.unit_number
        wing_code = unit.wing.code if unit.wing else ''
        unit.delete()
        messages.success(request, f"Flat {unit_num} ({wing_code}) has been deleted successfully.")
        return redirect('properties:units')
    return redirect('properties:unit_detail', pk=unit.pk)


@login_required
def delete_resident_view(request, pk):
    """Delete/Unlink a resident profile (Admin/Committee only)."""
    user = get_object_or_404(User, pk=pk)
    if not (request.user.is_society_admin or request.user.is_committee_member):
        messages.error(request, "Permission Denied: Only Society Admins and Committee members can remove residents.")
        return redirect('properties:directory')

    if request.method == 'POST':
        name = user.full_name
        Unit.objects.filter(owner=user).update(owner=None, occupancy_status=Unit.OccupancyStatus.VACANT)
        Unit.objects.filter(primary_resident=user).update(primary_resident=None, occupancy_status=Unit.OccupancyStatus.VACANT)
        user.delete()
        messages.success(request, f"Resident {name} has been removed from the society directory.")
        return redirect('properties:directory')
    return redirect('properties:directory')


@login_required
def delete_vehicle_view(request, pk):
    """Delete a registered vehicle (Owner or Admin/Committee)."""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if not (request.user.is_society_admin or request.user.is_committee_member or vehicle.owner == request.user):
        messages.error(request, "Permission Denied: You cannot delete this vehicle record.")
        return redirect('properties:vehicles')

    if request.method == 'POST':
        plate = vehicle.license_plate
        vehicle.delete()
        messages.success(request, f"Vehicle {plate} has been removed.")
        return redirect('properties:vehicles')
    return redirect('properties:vehicles')


@login_required
def delete_domestic_staff_view(request, pk):
    """Delete daily helper / domestic staff (Admin/Committee)."""
    staff = get_object_or_404(DomesticStaff, pk=pk)
    if not (request.user.is_society_admin or request.user.is_committee_member):
        messages.error(request, "Permission Denied: Only Admins/Committee can delete staff records.")
        return redirect('properties:staff')

    if request.method == 'POST':
        name = staff.name
        staff.delete()
        messages.success(request, f"Helper {name} record has been deleted.")
        return redirect('properties:staff')
    return redirect('properties:staff')


@login_required
def delete_move_request_view(request, pk):
    """Delete/Cancel a move-in/out request."""
    move_req = get_object_or_404(MoveInOutRequest, pk=pk)
    if not (request.user.is_society_admin or request.user.is_committee_member or move_req.resident == request.user):
        messages.error(request, "Permission Denied: You cannot delete this move request.")
        return redirect('properties:move_requests')

    if request.method == 'POST':
        move_req.delete()
        messages.success(request, "Move request has been cancelled and removed.")
        return redirect('properties:move_requests')
    return redirect('properties:move_requests')


@login_required
def delete_violation_view(request, pk):
    """Delete/Dismiss a rule violation report."""
    violation = get_object_or_404(RuleViolationReport, pk=pk)
    if not (request.user.is_society_admin or request.user.is_committee_member or violation.reported_by == request.user):
        messages.error(request, "Permission Denied: You cannot delete this violation report.")
        return redirect('properties:violations')

    if request.method == 'POST':
        violation.delete()
        messages.success(request, "Violation report has been removed.")
        return redirect('properties:violations')
    return redirect('properties:violations')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta, time
from decimal import Decimal

from .models import Amenity, AmenityBooking, EVChargingStation, EVChargingSession
from .forms import AmenityBookingForm
from apps.properties.models import Unit, Vehicle

@login_required
def amenity_list_view(request):
    """Browse society amenities, view photos, rules, and booking availability."""
    amenities = Amenity.objects.filter(is_active=True)
    category_filter = request.GET.get('category', '')

    if category_filter:
        amenities = amenities.filter(category=category_filter)

    return render(request, 'amenities/amenity_list.html', {
        'amenities': amenities,
        'selected_category': category_filter,
    })


@login_required
def amenity_detail_view(request, slug):
    """Detailed view of an amenity with calendar slots and instant booking form."""
    amenity = get_object_or_404(Amenity, slug=slug, is_active=True)
    today = timezone.now().date()
    upcoming_bookings = amenity.bookings.filter(
        booking_date__gte=today,
        status__in=[AmenityBooking.Status.CONFIRMED, AmenityBooking.Status.PENDING]
    ).order_by('booking_date', 'start_time')[:10]

    user_flats = request.user.resident_flats.all() | request.user.owned_units.all()
    if request.user.is_society_admin or request.user.is_committee_member:
        user_flats = Unit.objects.all()

    if request.method == 'POST':
        form = AmenityBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.resident = request.user
            booking.amenity = amenity

            # Check time conflict
            conflict = AmenityBooking.objects.filter(
                amenity=amenity,
                booking_date=booking.booking_date,
                status=AmenityBooking.Status.CONFIRMED,
                start_time__lt=booking.end_time,
                end_time__gt=booking.start_time
            ).exists()

            if conflict:
                messages.error(request, f"Selected slot ({booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}) is already reserved on {booking.booking_date}.")
            else:
                dt_start = datetime.combine(booking.booking_date, booking.start_time)
                dt_end = datetime.combine(booking.booking_date, booking.end_time)
                duration_hours = max(1.0, (dt_end - dt_start).total_seconds() / 3600.0)
                booking.total_fee = Decimal(str(amenity.hourly_rate)) * Decimal(str(duration_hours))

                if amenity.requires_approval:
                    booking.status = AmenityBooking.Status.PENDING
                    messages.info(request, f"Booking request submitted for {amenity.name}! Awaiting committee approval.")
                else:
                    booking.status = AmenityBooking.Status.CONFIRMED
                    messages.success(request, f"Booking Confirmed for {amenity.name} on {booking.booking_date}!")

                booking.save()
                return redirect('amenities:my_bookings')
    else:
        form = AmenityBookingForm(initial={'amenity': amenity, 'booking_date': today})
        form.fields['unit'].queryset = user_flats
        form.fields['amenity'].widget = forms.HiddenInput()

    return render(request, 'amenities/amenity_detail.html', {
        'amenity': amenity,
        'upcoming_bookings': upcoming_bookings,
        'form': form,
    })


@login_required
def my_bookings_view(request):
    """View resident's amenity booking reservations and EV sessions."""
    bookings = AmenityBooking.objects.filter(resident=request.user).select_related('amenity', 'unit')
    ev_sessions = EVChargingSession.objects.filter(user=request.user).select_related('station', 'unit')
    return render(request, 'amenities/my_bookings.html', {
        'bookings': bookings,
        'ev_sessions': ev_sessions,
    })


@login_required
def cancel_booking_view(request, pk):
    """Cancel an active reservation."""
    booking = get_object_or_404(AmenityBooking, pk=pk)
    if booking.resident != request.user and not (request.user.is_society_admin or request.user.is_committee_member):
        messages.error(request, "Permission denied.")
        return redirect('amenities:my_bookings')

    booking.status = AmenityBooking.Status.CANCELLED
    booking.save()
    messages.success(request, f"Booking for {booking.amenity.name} has been cancelled.")
    return redirect('amenities:my_bookings')


@login_required
def manage_bookings_view(request):
    """Committee approval panel for facility bookings."""
    if not (request.user.is_society_admin or request.user.is_committee_member):
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    pending_bookings = AmenityBooking.objects.filter(status=AmenityBooking.Status.PENDING).select_related('amenity', 'resident', 'unit')
    all_bookings = AmenityBooking.objects.select_related('amenity', 'resident', 'unit').order_by('-booking_date')[:30]

    action = request.POST.get('action')
    booking_id = request.POST.get('booking_id')

    if request.method == 'POST' and booking_id:
        booking = get_object_or_404(AmenityBooking, pk=booking_id)
        if action == 'approve':
            booking.status = AmenityBooking.Status.CONFIRMED
            booking.save()
            messages.success(request, f"Booking #{booking.id} for {booking.resident.full_name} approved!")
        elif action == 'reject':
            booking.status = AmenityBooking.Status.REJECTED
            booking.rejection_reason = request.POST.get('reason', 'Schedule unavailable.')
            booking.save()
            messages.warning(request, f"Booking #{booking.id} rejected.")

        return redirect('amenities:manage')

    return render(request, 'amenities/manage_bookings.html', {
        'pending_bookings': pending_bookings,
        'all_bookings': all_bookings,
    })


@login_required
def ev_charging_view(request):
    """EV Fast Charging Station Booker & Status."""
    stations = EVChargingStation.objects.filter(is_active=True)
    user_flats = request.user.resident_flats.all() | request.user.owned_units.all()
    user_vehicles = request.user.vehicles.all()

    if request.method == 'POST':
        station_id = request.POST.get('station_id')
        station = get_object_or_404(EVChargingStation, id=station_id)
        unit_id = request.POST.get('unit_id')
        unit = get_object_or_404(Unit, id=unit_id)
        vehicle_id = request.POST.get('vehicle_id')
        vehicle = Vehicle.objects.filter(id=vehicle_id).first() if vehicle_id else None
        
        hours = int(request.POST.get('hours', 2))
        start_t = time(timezone.now().hour, 0)
        end_t = time(min(23, timezone.now().hour + hours), 0)

        # Estimate units & cost
        est_units = float(station.power_kw) * hours * 0.85
        total_cost = Decimal(str(est_units)) * station.kwh_rate

        session = EVChargingSession.objects.create(
            station=station,
            user=request.user,
            unit=unit,
            vehicle=vehicle,
            booking_date=timezone.now().date(),
            start_time=start_t,
            end_time=end_t,
            units_consumed_kwh=Decimal(str(round(est_units, 2))),
            total_cost=Decimal(str(round(total_cost, 2))),
            status=EVChargingSession.SessionStatus.ACTIVE
        )
        messages.success(request, f"EV Charging initiated at {station.station_name}! Estimated cost: ₹{total_cost:,.2f}")
        return redirect('amenities:ev_charging')

    recent_sessions = EVChargingSession.objects.filter(user=request.user).select_related('station', 'unit')[:5]

    return render(request, 'amenities/ev_charging.html', {
        'stations': stations,
        'user_flats': user_flats,
        'user_vehicles': user_vehicles,
        'recent_sessions': recent_sessions,
    })


@login_required
def delete_booking_view(request, pk):
    """Delete an amenity booking reservation (Resident or Admin/Committee)."""
    booking = get_object_or_404(AmenityBooking, pk=pk)
    if not (request.user.is_society_admin or request.user.is_committee_member or booking.resident == request.user):
        messages.error(request, "Permission Denied: You cannot delete this booking.")
        return redirect('amenities:my_bookings')

    if request.method == 'POST':
        amenity_name = booking.amenity.name
        booking.delete()
        messages.success(request, f"Booking for {amenity_name} has been deleted.")
        if request.user.is_society_admin or request.user.is_committee_member:
            return redirect('amenities:manage')
        return redirect('amenities:my_bookings')
    return redirect('amenities:my_bookings')


@login_required
def delete_ev_session_view(request, pk):
    """Delete or cancel an EV Charging session."""
    session = get_object_or_404(EVChargingSession, pk=pk)
    if not (request.user.is_society_admin or request.user.is_committee_member or session.user == request.user):
        messages.error(request, "Permission Denied: You cannot delete this charging session.")
        return redirect('amenities:ev_charging')

    if request.method == 'POST':
        station_name = session.station.station_name
        session.delete()
        messages.success(request, f"EV Charging record at {station_name} has been removed.")
        return redirect('amenities:ev_charging')
    return redirect('amenities:ev_charging')


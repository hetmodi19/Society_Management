from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
import uuid

from .models import MaintenanceTicket, TicketComment
from .forms import MaintenanceTicketForm, TicketCommentForm, StaffAssignmentForm, TicketRatingForm
from apps.properties.models import Unit
from apps.accounts.models import User

@login_required
def ticket_list_view(request):
    """View complaints list with role isolation (Admins view all; Staff view assigned; Residents view own)."""
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')

    if request.user.is_society_admin or request.user.is_committee_member:
        tickets = MaintenanceTicket.objects.select_related('resident', 'unit', 'assigned_staff').all()
    elif request.user.is_facility_staff:
        tickets = MaintenanceTicket.objects.filter(
            Q(assigned_staff=request.user) | Q(status=MaintenanceTicket.Status.OPEN)
        ).select_related('resident', 'unit', 'assigned_staff')
    else:
        # Resident isolation
        tickets = MaintenanceTicket.objects.filter(
            Q(resident=request.user) |
            Q(unit__owner=request.user) |
            Q(unit__primary_resident=request.user)
        ).select_related('resident', 'unit', 'assigned_staff').distinct()

    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if category_filter:
        tickets = tickets.filter(category=category_filter)

    open_count = tickets.filter(status=MaintenanceTicket.Status.OPEN).count()
    progress_count = tickets.filter(status=MaintenanceTicket.Status.IN_PROGRESS).count()
    resolved_count = tickets.filter(status=MaintenanceTicket.Status.RESOLVED).count()

    return render(request, 'helpdesk/ticket_list.html', {
        'tickets': tickets,
        'selected_status': status_filter,
        'selected_category': category_filter,
        'open_count': open_count,
        'progress_count': progress_count,
        'resolved_count': resolved_count,
    })


@login_required
def create_ticket_view(request):
    """Log a new maintenance request or issue."""
    user_flats = (request.user.resident_flats.all() | request.user.owned_units.all()).distinct()
    if request.user.is_society_admin or request.user.is_committee_member:
        user_flats = Unit.objects.all()

    if request.method == 'POST':
        form = MaintenanceTicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.resident = request.user
            
            # Security verification
            if not (request.user.is_society_admin or ticket.unit in user_flats):
                messages.error(request, "You can only raise service complaints for your assigned flat.")
                return redirect('helpdesk:tickets')

            ticket.ticket_number = f"TCK-{timezone.now().year}-{uuid.uuid4().hex[:6].upper()}"
            ticket.save()

            messages.success(request, f"Service Complaint #{ticket.ticket_number} created successfully! Technician will be assigned.")
            return redirect('helpdesk:detail', pk=ticket.pk)
    else:
        form = MaintenanceTicketForm()
        form.fields['unit'].queryset = user_flats

    return render(request, 'helpdesk/create_ticket.html', {'form': form})


@login_required
def ticket_detail_view(request, pk):
    """Ticket details, conversation history, and status updates."""
    ticket = get_object_or_404(MaintenanceTicket.objects.select_related('resident', 'unit', 'assigned_staff'), pk=pk)

    # Privacy check
    is_authorized = (
        request.user.is_society_admin or
        request.user.is_committee_member or
        ticket.assigned_staff == request.user or
        ticket.resident == request.user or
        ticket.unit.owner == request.user or
        ticket.unit.primary_resident == request.user
    )
    if not is_authorized:
        messages.error(request, "Access Denied: You cannot view this ticket.")
        return redirect('helpdesk:tickets')

    if request.method == 'POST' and 'comment_submit' in request.POST:
        comment_form = TicketCommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            comm = comment_form.save(commit=False)
            comm.ticket = ticket
            comm.author = request.user
            comm.save()
            messages.success(request, "Comment added.")
            return redirect('helpdesk:detail', pk=ticket.pk)
    else:
        comment_form = TicketCommentForm()

    comments = ticket.comments.select_related('author').all()
    assign_form = StaffAssignmentForm(instance=ticket) if (request.user.is_society_admin or request.user.is_committee_member) else None
    rating_form = TicketRatingForm(instance=ticket) if ticket.status == MaintenanceTicket.Status.RESOLVED else None

    return render(request, 'helpdesk/ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
        'assign_form': assign_form,
        'rating_form': rating_form,
    })


@login_required
def update_ticket_status_view(request, pk):
    """Update ticket workflow status and technician assignment."""
    ticket = get_object_or_404(MaintenanceTicket, pk=pk)

    if not (request.user.is_society_admin or request.user.is_committee_member or ticket.assigned_staff == request.user):
        messages.error(request, "Permission denied.")
        return redirect('helpdesk:detail', pk=ticket.pk)

    new_status = request.POST.get('status')
    staff_id = request.POST.get('assigned_staff')
    resolution_notes = request.POST.get('resolution_notes', '')

    if new_status:
        ticket.status = new_status
        if new_status == MaintenanceTicket.Status.RESOLVED:
            ticket.resolved_at = timezone.now()
            ticket.resolution_notes = resolution_notes

    if staff_id and (request.user.is_society_admin or request.user.is_committee_member):
        ticket.assigned_staff = User.objects.filter(id=staff_id, role=User.Role.STAFF).first()

    ticket.save()
    messages.success(request, f"Ticket #{ticket.ticket_number} updated to {ticket.get_status_display()}.")
    return redirect('helpdesk:detail', pk=ticket.pk)


@login_required
def rate_ticket_view(request, pk):
    """Resident leaves rating and feedback for completed technician work."""
    ticket = get_object_or_404(MaintenanceTicket, pk=pk)

    if ticket.resident != request.user and ticket.unit.primary_resident != request.user:
        messages.error(request, "Only the resident who logged the complaint can rate this service.")
        return redirect('helpdesk:detail', pk=ticket.pk)

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        feedback = request.POST.get('resident_feedback', '').strip()
        ticket.rating = rating
        ticket.resident_feedback = feedback
        ticket.save()
        messages.success(request, "Thank you for your feedback! Rating recorded.")

    return redirect('helpdesk:detail', pk=ticket.pk)

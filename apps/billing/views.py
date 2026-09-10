from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import uuid

from django.db.models import Q
from .models import MaintenanceBill, BillPayment, MaintenanceConfig, SocietyExpense
from .forms import BatchBillGenerationForm, SocietyExpenseForm, MaintenanceConfigForm
from apps.properties.models import Unit
from apps.accounts.decorators import committee_required, admin_required, financial_required

@login_required
def bill_list_view(request):
    """View maintenance bills. Committee views all bills; Residents only view their own unit invoices."""
    status_filter = request.GET.get('status', '')
    month_filter = request.GET.get('month', '')

    if request.user.is_society_admin or request.user.is_committee_member:
        bills = MaintenanceBill.objects.select_related('unit', 'unit__wing', 'resident').all()
    else:
        # Resident/Tenant isolation
        bills = MaintenanceBill.objects.filter(
            Q(resident=request.user) |
            Q(unit__owner=request.user) |
            Q(unit__primary_resident=request.user)
        ).select_related('unit', 'unit__wing', 'resident').distinct()

    if status_filter:
        bills = bills.filter(status=status_filter)

    # Financial statistics
    if request.user.is_society_admin or request.user.is_committee_member:
        all_bills = MaintenanceBill.objects.all()
    else:
        all_bills = bills

    total_billed = sum(b.total_amount for b in all_bills)
    total_collected = sum(b.paid_amount for b in all_bills)
    total_pending = total_billed - total_collected

    return render(request, 'billing/bill_list.html', {
        'bills': bills,
        'selected_status': status_filter,
        'total_billed': total_billed,
        'total_collected': total_collected,
        'total_pending': total_pending,
    })


@login_required
def bill_detail_view(request, pk):
    """View detailed tax breakdown and payment history for a maintenance bill."""
    bill = get_object_or_404(MaintenanceBill.objects.select_related('unit', 'unit__wing', 'resident'), pk=pk)

    # Security check: User must be Admin, Committee, or Owner/Tenant of that flat
    is_authorized = (
        request.user.is_society_admin or
        request.user.is_committee_member or
        bill.resident == request.user or
        bill.unit.owner == request.user or
        bill.unit.primary_resident == request.user
    )
    if not is_authorized:
        messages.error(request, "Access Denied: You cannot view invoices for other flats.")
        return redirect('billing:bills')

    payments = bill.payments.filter(payment_status=BillPayment.PaymentStatus.SUCCESS)

    return render(request, 'billing/bill_detail.html', {
        'bill': bill,
        'payments': payments,
    })


@login_required
def pay_bill_view(request, pk):
    """Checkout gateway for maintenance bills (UPI QR Code, Card, NetBanking)."""
    bill = get_object_or_404(MaintenanceBill, pk=pk)

    is_authorized = (
        request.user.is_society_admin or
        bill.resident == request.user or
        bill.unit.owner == request.user or
        bill.unit.primary_resident == request.user
    )
    if not is_authorized:
        messages.error(request, "Access Denied: You cannot make payments on behalf of other flats.")
        return redirect('billing:bills')

    if bill.status == MaintenanceBill.Status.PAID:
        messages.info(request, "This maintenance invoice is already settled in full.")
        return redirect('billing:detail', pk=bill.pk)

    if request.method == 'POST':
        method = request.POST.get('payment_method', 'UPI')
        amount_to_pay = Decimal(str(request.POST.get('amount', str(bill.remaining_due))))

        txn_id = f"TXN-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        receipt_no = f"RCPT-{timezone.now().year}-{uuid.uuid4().hex[:8].upper()}"

        payment = BillPayment.objects.create(
            bill=bill,
            transaction_id=txn_id,
            receipt_number=receipt_no,
            payer=request.user,
            amount=amount_to_pay,
            payment_method=method,
            payment_status=BillPayment.PaymentStatus.SUCCESS,
            gateway_reference=request.POST.get('gateway_ref', f"GATEWAY-OK-{uuid.uuid4().hex[:8]}"),
            remarks="Online instant checkout payment"
        )

        bill.paid_amount += payment.amount
        bill.update_status()
        bill.save()

        messages.success(request, f"Payment of ₹{amount_to_pay:,.2f} completed successfully! Receipt #{receipt_no} generated.")
        return redirect('billing:receipt', pk=payment.pk)

    return render(request, 'billing/pay_checkout.html', {'bill': bill})


@login_required
def receipt_view(request, pk):
    """View official payment tax receipt."""
    payment = get_object_or_404(BillPayment.objects.select_related('bill', 'bill__unit', 'payer'), pk=pk)

    is_authorized = (
        request.user.is_society_admin or
        request.user.is_committee_member or
        payment.payer == request.user or
        payment.bill.unit.owner == request.user or
        payment.bill.unit.primary_resident == request.user
    )
    if not is_authorized:
        messages.error(request, "Access Denied: You cannot view this receipt.")
        return redirect('billing:bills')

    return render(request, 'billing/receipt.html', {'payment': payment})


@committee_required
def financial_ledger_view(request):
    """Financial ledger & society audited expense tracker for Committee."""
    expenses = SocietyExpense.objects.select_related('recorded_by', 'approved_by').all()
    all_bills = MaintenanceBill.objects.all()

    total_income = sum(b.paid_amount for b in all_bills)
    total_expense = sum(e.amount for e in expenses if e.is_approved)
    net_reserve = total_income - total_expense

    if request.method == 'POST':
        exp_form = SocietyExpenseForm(request.POST, request.FILES)
        if exp_form.is_valid():
            expense = exp_form.save(commit=False)
            expense.recorded_by = request.user
            if request.user.is_society_admin:
                expense.is_approved = True
                expense.approved_by = request.user
            expense.save()
            messages.success(request, f"Expense '{expense.title}' recorded.")
            return redirect('billing:ledger')
    else:
        exp_form = SocietyExpenseForm()

    return render(request, 'billing/financial_ledger.html', {
        'expenses': expenses,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_reserve': net_reserve,
        'exp_form': exp_form,
    })


@financial_required
def generate_batch_bills_view(request):
    """Batch monthly bill generator for Society Admin."""
    if request.method == 'POST':
        form = BatchBillGenerationForm(request.POST)
        if form.is_valid():
            billing_month = form.cleaned_data['billing_month']
            due_date = form.cleaned_data['due_date']
            config = MaintenanceConfig.objects.first() or MaintenanceConfig()

            units = Unit.objects.filter(occupancy_status__in=[Unit.OccupancyStatus.OWNER, Unit.OccupancyStatus.TENANT])
            created_count = 0

            for u in units:
                existing = MaintenanceBill.objects.filter(unit=u, billing_month=billing_month).first()
                if not existing:
                    base_rate = config.base_rate_per_sqft or Decimal('3.50')
                    base = Decimal(str(u.square_feet)) * base_rate
                    sinking = (Decimal(str(u.square_feet)) * config.sinking_fund_rate) if config.sinking_fund_rate else Decimal('500.00')
                    water = config.water_fixed_charge or Decimal('400.00')
                    amenity = config.fixed_amenities_fee or Decimal('500.00')
                    
                    car_count = u.vehicles.filter(vehicle_type='CAR').count()
                    parking = (config.parking_slot_fee or Decimal('300.00')) * car_count

                    total = base + sinking + water + amenity + parking
                    bill_no = f"INV-{billing_month.strftime('%Y%m')}-{u.unit_number.replace('-', '')}"

                    res_target = u.primary_resident or u.owner

                    MaintenanceBill.objects.create(
                        bill_number=bill_no,
                        unit=u,
                        resident=res_target,
                        billing_month=billing_month,
                        due_date=due_date,
                        base_charge=base,
                        sinking_fund=sinking,
                        parking_charge=parking,
                        water_charge=water,
                        amenity_charge=amenity,
                        total_amount=total,
                        status=MaintenanceBill.Status.UNPAID
                    )
                    created_count += 1

            messages.success(request, f"Generated {created_count} monthly maintenance invoices for {billing_month.strftime('%B %Y')}!")
            return redirect('billing:bills')
    else:
        next_month = (timezone.now().date().replace(day=1) + timedelta(days=32)).replace(day=1)
        form = BatchBillGenerationForm(initial={
            'billing_month': next_month,
            'due_date': next_month + timedelta(days=15)
        })

    return render(request, 'billing/generate_bills.html', {'form': form})


@login_required
def delete_bill_view(request, pk):
    """Delete a maintenance bill invoice (Admin/Committee only)."""
    bill = get_object_or_404(MaintenanceBill, pk=pk)
    if not (request.user.is_society_admin or request.user.is_committee_member):
        messages.error(request, "Permission Denied: Only Society Admins and Committee members can delete invoices.")
        return redirect('billing:bills')

    if request.method == 'POST':
        bill_num = bill.bill_number
        bill.delete()
        messages.success(request, f"Maintenance Invoice {bill_num} has been deleted.")
        return redirect('billing:bills')
    return redirect('billing:detail', pk=bill.pk)


@committee_required
def delete_expense_view(request, pk):
    """Delete a society ledger expense entry (Committee/Admin only)."""
    expense = get_object_or_404(SocietyExpense, pk=pk)
    if request.method == 'POST':
        title = expense.title
        expense.delete()
        messages.success(request, f"Expense '{title}' has been removed from the ledger.")
        return redirect('billing:ledger')
    return redirect('billing:ledger')


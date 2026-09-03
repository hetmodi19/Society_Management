from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

class MaintenanceConfig(models.Model):
    name = models.CharField(max_length=100, default='Standard Society Billing Policy')
    base_rate_per_sqft = models.DecimalField(max_digits=8, decimal_places=2, default=3.50, help_text=_("Rate per Sq. Ft. per month"))
    sinking_fund_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.50, help_text=_("Sinking fund per Sq. Ft."))
    fixed_amenities_fee = models.DecimalField(max_digits=8, decimal_places=2, default=500.00, help_text=_("Fixed clubhouse/security fee"))
    parking_slot_fee = models.DecimalField(max_digits=8, decimal_places=2, default=300.00, help_text=_("Fee per vehicle parking slot"))
    water_fixed_charge = models.DecimalField(max_digits=8, decimal_places=2, default=400.00)
    late_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00, help_text=_("Penalty %% after due date"))
    payment_grace_days = models.PositiveIntegerField(default=10, help_text=_("Days to pay from generation before late fee"))
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (Sqft: ₹{self.base_rate_per_sqft}/sqft)"


class MaintenanceBill(models.Model):
    class Status(models.TextChoices):
        UNPAID = 'UNPAID', _('Unpaid')
        PAID = 'PAID', _('Fully Paid')
        PARTIAL = 'PARTIAL', _('Partially Paid')
        OVERDUE = 'OVERDUE', _('Overdue')

    bill_number = models.CharField(max_length=50, unique=True)
    unit = models.ForeignKey('properties.Unit', on_delete=models.CASCADE, related_name='maintenance_bills')
    resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resident_bills')
    billing_month = models.DateField(help_text=_("First day of the billing month e.g., 2026-09-01"))
    due_date = models.DateField()

    # Itemized Breakdown
    base_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sinking_fund = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    parking_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    water_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amenity_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    late_penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNPAID)
    generated_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-billing_month', 'unit__unit_number']
        unique_together = ('unit', 'billing_month')

    def __str__(self):
        return f"{self.bill_number} | {self.unit.unit_number} - ₹{self.total_amount} ({self.get_status_display()})"

    @property
    def remaining_due(self):
        from decimal import Decimal
        total = Decimal(str(self.total_amount or 0))
        paid = Decimal(str(self.paid_amount or 0))
        return max(Decimal('0.00'), total - paid)

    @property
    def is_past_due(self):
        return self.status != self.Status.PAID and self.due_date < timezone.now().date()

    def update_status(self):
        if self.paid_amount >= self.total_amount:
            self.status = self.Status.PAID
            if not self.paid_at:
                self.paid_at = timezone.now()
        elif self.paid_amount > 0:
            self.status = self.Status.PARTIAL
        elif self.is_past_due:
            self.status = self.Status.OVERDUE
        else:
            self.status = self.Status.UNPAID


class BillPayment(models.Model):
    class PaymentMethod(models.TextChoices):
        UPI = 'UPI', _('UPI / Instant QR Code (GooglePay, PhonePe, Paytm)')
        CARD = 'CARD', _('Debit / Credit Card (Visa, MasterCard, Amex)')
        NETBANKING = 'NETBANKING', _('Net Banking / NEFT / IMPS')
        CASH = 'CASH', _('Cash Payment to Office')
        CHEQUE = 'CHEQUE', _('Cheque Deposit')

    class PaymentStatus(models.TextChoices):
        SUCCESS = 'SUCCESS', _('Payment Successful')
        PENDING = 'PENDING', _('Processing / Verification')
        FAILED = 'FAILED', _('Failed')

    bill = models.ForeignKey(MaintenanceBill, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=100, unique=True)
    receipt_number = models.CharField(max_length=50, unique=True)
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='payments_made')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PaymentMethod.choices, default=PaymentMethod.UPI)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.SUCCESS)
    gateway_reference = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(default=timezone.now)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Receipt #{self.receipt_number} - ₹{self.amount} for {self.bill.unit.unit_number}"


class SocietyExpense(models.Model):
    class Category(models.TextChoices):
        ELECTRICITY = 'ELECTRICITY', _('Common Area Electricity & Generator Fuel')
        WATER_SUPPLY = 'WATER_SUPPLY', _('Municipal Water Supply & Tankers')
        SECURITY = 'SECURITY', _('Security Agency Contract')
        HOUSEKEEPING = 'HOUSEKEEPING', _('Housekeeping & Waste Management')
        LIFT_AMC = 'LIFT_AMC', _('Elevator/Lift AMC Maintenance')
        GARDENING = 'GARDENING', _('Gardening & Landscape Care')
        REPAIRS = 'REPAIRS', _('Civil, Plumbing & Electrical Repairs')
        FESTIVAL = 'FESTIVAL', _('Festival, Cultural & Event Celebrations')
        SALARIES = 'SALARIES', _('Staff Salaries & Bonuses')
        ADMIN_EXPENSE = 'ADMIN_EXPENSE', _('Office Administration & Audit Fees')
        MISC = 'MISC', _('Miscellaneous Society Expenses')

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.REPAIRS)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField(default=timezone.now)
    vendor_name = models.CharField(max_length=150, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    is_approved = models.BooleanField(default=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses')
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_expenses')
    receipt_doc = models.FileField(upload_to='expenses/receipts/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.title} - ₹{self.amount} ({self.get_category_display()})"

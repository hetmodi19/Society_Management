from django.contrib import admin
from .models import MaintenanceConfig, MaintenanceBill, BillPayment, SocietyExpense

@admin.register(MaintenanceConfig)
class MaintenanceConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_rate_per_sqft', 'sinking_fund_rate', 'fixed_amenities_fee', 'parking_slot_fee', 'is_active')

@admin.register(MaintenanceBill)
class MaintenanceBillAdmin(admin.ModelAdmin):
    list_display = ('bill_number', 'unit', 'resident', 'billing_month', 'total_amount', 'paid_amount', 'status', 'due_date')
    list_filter = ('status', 'billing_month')
    search_fields = ('bill_number', 'unit__unit_number', 'resident__username', 'resident__first_name', 'resident__last_name')

@admin.register(BillPayment)
class BillPaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'bill', 'payer', 'amount', 'payment_method', 'payment_status', 'payment_date')
    list_filter = ('payment_method', 'payment_status')
    search_fields = ('receipt_number', 'transaction_id', 'bill__bill_number')

@admin.register(SocietyExpense)
class SocietyExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'amount', 'expense_date', 'vendor_name', 'is_approved')
    list_filter = ('category', 'is_approved', 'expense_date')
    search_fields = ('title', 'vendor_name', 'invoice_number')

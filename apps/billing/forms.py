from django import forms
from .models import MaintenanceBill, BillPayment, SocietyExpense, MaintenanceConfig

class BillPaymentForm(forms.ModelForm):
    class Meta:
        model = BillPayment
        fields = ('amount', 'payment_method', 'gateway_reference', 'remarks')
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control form-select'}),
            'gateway_reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UPI Ref / UTR / Card Auth Code'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional payment notes'}),
        }


class SocietyExpenseForm(forms.ModelForm):
    class Meta:
        model = SocietyExpense
        fields = ('title', 'category', 'amount', 'expense_date', 'vendor_name', 'invoice_number', 'description')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Expense description/item'}),
            'category': forms.Select(attrs={'class': 'form-control form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vendor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier/Contractor'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bill / Invoice #'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MaintenanceConfigForm(forms.ModelForm):
    class Meta:
        model = MaintenanceConfig
        fields = '__all__'


class BatchBillGenerationForm(forms.Form):
    billing_month = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), label="Billing Month (1st of month)")
    due_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), label="Payment Due Date")


GenerateBillsForm = BatchBillGenerationForm

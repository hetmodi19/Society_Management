from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import VisitorLog, PreApprovedPass, ParcelLog, SOSAlert

class VisitorEntryForm(forms.ModelForm):
    class Meta:
        model = VisitorLog
        fields = ('visitor_name', 'phone_number', 'visitor_type', 'unit', 'vehicle_number', 'purpose')
        widgets = {
            'visitor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Visitor's Full Name"}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Visitor Mobile #"}),
            'visitor_type': forms.Select(attrs={'class': 'form-control form-select'}),
            'unit': forms.Select(attrs={'class': 'form-control form-select'}),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "e.g. MH-01-AB-1234 (optional)"}),
            'purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Reason for visiting"}),
        }


class PreApprovedPassForm(forms.ModelForm):
    duration_hours = forms.IntegerField(initial=8, min_value=1, max_value=72, widget=forms.NumberInput(attrs={'class': 'form-control'}), label="Validity Duration (Hours)")

    class Meta:
        model = PreApprovedPass
        fields = ('visitor_name', 'visitor_phone', 'unit', 'purpose')
        widgets = {
            'visitor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Guest Name"}),
            'visitor_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Guest Phone (Optional)"}),
            'unit': forms.Select(attrs={'class': 'form-control form-select'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "e.g. Dinner Party, Delivery, Plumber"}),
        }


class ParcelLogForm(forms.ModelForm):
    class Meta:
        model = ParcelLog
        fields = ('unit', 'recipient_name', 'courier_company', 'tracking_number')
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-control form-select'}),
            'recipient_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resident Name'}),
            'courier_company': forms.Select(attrs={'class': 'form-control form-select'}),
            'tracking_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Packet ID / Tracking #'}),
        }


class SOSAlertForm(forms.ModelForm):
    class Meta:
        model = SOSAlert
        fields = ('alert_type', 'location_details', 'message')
        widgets = {
            'alert_type': forms.Select(attrs={'class': 'form-control form-select alert-select'}),
            'location_details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Flat A-304 / Clubhouse Lift 2'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Details of emergency...'}),
        }

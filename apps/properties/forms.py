from django import forms
from .models import Unit, Vehicle, DomesticStaff, Wing, MoveInOutRequest, RuleViolationReport

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ('wing', 'unit_number', 'floor', 'unit_type', 'square_feet', 'occupancy_status', 'owner', 'primary_resident', 'parking_slot_number', 'intercom_extension')
        widgets = {
            'wing': forms.Select(attrs={'class': 'form-control form-select'}),
            'unit_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. A-402'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_type': forms.Select(attrs={'class': 'form-control form-select'}),
            'square_feet': forms.NumberInput(attrs={'class': 'form-control'}),
            'occupancy_status': forms.Select(attrs={'class': 'form-control form-select'}),
            'owner': forms.Select(attrs={'class': 'form-control form-select'}),
            'primary_resident': forms.Select(attrs={'class': 'form-control form-select'}),
            'parking_slot_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. P-A402'}),
            'intercom_extension': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1402'}),
        }


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ('unit', 'vehicle_type', 'license_plate', 'make_model', 'parking_slot', 'rfid_tag')
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-control form-select'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-control form-select'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MH-02-AB-1234'}),
            'make_model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tesla Model 3 / Honda City'}),
            'parking_slot': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. B2-Slot 14'}),
            'rfid_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RFID Sticker Code (Optional)'}),
        }


class DomesticStaffForm(forms.ModelForm):
    class Meta:
        model = DomesticStaff
        fields = ('name', 'role_type', 'phone_number', 'passcode', 'assigned_units', 'working_hours')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'role_type': forms.Select(attrs={'class': 'form-control form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 555-0199'}),
            'passcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '4-digit Gate Code e.g. 7821'}),
            'assigned_units': forms.SelectMultiple(attrs={'class': 'form-control', 'size': 5}),
            'working_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '08:00 AM - 05:00 PM'}),
        }


class MoveInOutRequestForm(forms.ModelForm):
    class Meta:
        model = MoveInOutRequest
        fields = ('unit', 'move_type', 'move_date', 'time_slot', 'service_lift_required', 'moving_company_name', 'vehicle_count', 'notes')
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-control form-select'}),
            'move_type': forms.Select(attrs={'class': 'form-control form-select'}),
            'move_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_slot': forms.Select(choices=[
                ('Morning (08:00 AM - 12:00 PM)', 'Morning (08:00 AM - 12:00 PM)'),
                ('Afternoon (12:00 PM - 04:00 PM)', 'Afternoon (12:00 PM - 04:00 PM)'),
                ('Evening (04:00 PM - 08:00 PM)', 'Evening (04:00 PM - 08:00 PM)')
            ], attrs={'class': 'form-control form-select'}),
            'service_lift_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'moving_company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Movers & Packers Name'}),
            'vehicle_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Special items (Piano, Safe, Furniture) or instructions...'}),
        }


class RuleViolationReportForm(forms.ModelForm):
    class Meta:
        model = RuleViolationReport
        fields = ('unit', 'violation_type', 'description', 'evidence_photo')
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-control form-select'}),
            'violation_type': forms.Select(attrs={'class': 'form-control form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the infraction or dispute...'}),
            'evidence_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

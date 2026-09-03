from django import forms
from .models import Amenity, AmenityBooking

class AmenityBookingForm(forms.ModelForm):
    class Meta:
        model = AmenityBooking
        fields = ('amenity', 'unit', 'booking_date', 'start_time', 'end_time', 'guest_count', 'purpose')
        widgets = {
            'amenity': forms.Select(attrs={'class': 'form-control form-select'}),
            'unit': forms.Select(attrs={'class': 'form-control form-select'}),
            'booking_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'guest_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event / activity description'}),
        }

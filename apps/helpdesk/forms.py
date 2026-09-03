from django import forms
from .models import MaintenanceTicket, TicketComment

class MaintenanceTicketForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTicket
        fields = ('title', 'category', 'priority', 'unit', 'description', 'photo')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief summary of the issue (e.g. Master bathroom tap leaking)'}),
            'category': forms.Select(attrs={'class': 'form-control form-select'}),
            'priority': forms.Select(attrs={'class': 'form-control form-select'}),
            'unit': forms.Select(attrs={'class': 'form-control form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the problem in detail...'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ('message', 'attachment')
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Write a response or update...'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }


class TicketStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTicket
        fields = ('status', 'assigned_staff', 'resolution_notes')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control form-select'}),
            'assigned_staff': forms.Select(attrs={'class': 'form-control form-select'}),
            'resolution_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Work completed notes...'}),
        }


class TicketRatingForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTicket
        fields = ('rating', 'resident_feedback')
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} Stars - {'Excellent' if i==5 else 'Good' if i==4 else 'Average' if i==3 else 'Poor' if i==2 else 'Terrible'}") for i in range(5, 0, -1)], attrs={'class': 'form-control form-select'}),
            'resident_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your feedback on the resolution...'}),
        }


StaffAssignmentForm = TicketStatusUpdateForm

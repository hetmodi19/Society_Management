from django.contrib import admin
from .models import VisitorLog, PreApprovedPass, ParcelLog, SOSAlert

@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('visitor_name', 'visitor_type', 'unit', 'host_resident', 'entry_time', 'exit_time', 'status', 'is_pre_approved')
    list_filter = ('visitor_type', 'status', 'is_pre_approved')
    search_fields = ('visitor_name', 'phone_number', 'unit__unit_number', 'vehicle_number')

@admin.register(PreApprovedPass)
class PreApprovedPassAdmin(admin.ModelAdmin):
    list_display = ('pass_code', 'visitor_name', 'unit', 'host_resident', 'valid_from', 'valid_until', 'is_used')
    list_filter = ('is_used',)
    search_fields = ('pass_code', 'visitor_name', 'unit__unit_number')

@admin.register(ParcelLog)
class ParcelLogAdmin(admin.ModelAdmin):
    list_display = ('recipient_name', 'unit', 'courier_company', 'tracking_number', 'received_at', 'is_collected')
    list_filter = ('courier_company', 'is_collected')
    search_fields = ('recipient_name', 'unit__unit_number', 'tracking_number')

@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display = ('alert_type', 'triggered_by', 'unit', 'is_resolved', 'created_at')
    list_filter = ('alert_type', 'is_resolved')
    search_fields = ('triggered_by__username', 'location_details', 'message')

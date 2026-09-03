from django.contrib import admin
from .models import Wing, Unit, ResidentUnitMapping, Vehicle, DomesticStaff

@admin.register(Wing)
class WingAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'total_floors', 'units_count', 'created_at')
    search_fields = ('name', 'code')

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'wing', 'floor', 'unit_type', 'square_feet', 'occupancy_status', 'primary_resident', 'parking_slot_number')
    list_filter = ('wing', 'occupancy_status', 'unit_type', 'floor')
    search_fields = ('unit_number', 'primary_resident__username', 'primary_resident__first_name', 'primary_resident__last_name', 'parking_slot_number')

@admin.register(ResidentUnitMapping)
class ResidentUnitMappingAdmin(admin.ModelAdmin):
    list_display = ('user', 'unit', 'relation_type', 'is_primary', 'is_active')
    list_filter = ('relation_type', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'unit__unit_number')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'make_model', 'vehicle_type', 'unit', 'owner', 'parking_slot', 'rfid_tag')
    list_filter = ('vehicle_type', 'is_active')
    search_fields = ('license_plate', 'make_model', 'unit__unit_number', 'owner__username')

@admin.register(DomesticStaff)
class DomesticStaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'role_type', 'phone_number', 'passcode', 'is_verified', 'is_active')
    list_filter = ('role_type', 'is_verified', 'is_active')
    search_fields = ('name', 'phone_number', 'passcode')

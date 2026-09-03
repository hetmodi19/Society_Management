from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ResidentProfile, StaffProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Society Info', {'fields': ('role', 'phone_number', 'alternate_phone', 'address', 'profile_picture', 'is_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Society Info', {'fields': ('role', 'email', 'phone_number')}),
    )

@admin.register(ResidentProfile)
class ResidentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'resident_type', 'intercom_number', 'blood_group', 'emergency_contact_name', 'emergency_contact_phone')
    list_filter = ('resident_type', 'blood_group')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'intercom_number')

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'badge_number', 'duty_shift', 'is_on_duty', 'rating')
    list_filter = ('specialization', 'is_on_duty')
    search_fields = ('user__username', 'badge_number')

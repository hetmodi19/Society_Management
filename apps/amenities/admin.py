from django.contrib import admin
from .models import Amenity, AmenityBooking

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'capacity', 'hourly_rate', 'open_time', 'close_time', 'is_active', 'requires_approval')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('category', 'is_active', 'requires_approval')
    search_fields = ('name', 'description')

@admin.register(AmenityBooking)
class AmenityBookingAdmin(admin.ModelAdmin):
    list_display = ('amenity', 'resident', 'unit', 'booking_date', 'start_time', 'end_time', 'total_fee', 'status')
    list_filter = ('status', 'booking_date', 'amenity')
    search_fields = ('resident__username', 'resident__first_name', 'amenity__name', 'unit__unit_number')

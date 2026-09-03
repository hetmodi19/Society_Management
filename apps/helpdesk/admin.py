from django.contrib import admin
from .models import MaintenanceTicket, TicketComment

@admin.register(MaintenanceTicket)
class MaintenanceTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'title', 'category', 'priority', 'status', 'resident', 'unit', 'assigned_staff', 'created_at')
    list_filter = ('category', 'priority', 'status')
    search_fields = ('ticket_number', 'title', 'unit__unit_number', 'resident__username')

@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'created_at')

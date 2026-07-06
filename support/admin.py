from django.contrib import admin
from .models import Complaint, Maintenance


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'staff', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['student__name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'room', 'staff', 'status', 'priority', 'scheduled_date', 'created_at']
    list_filter = ['status', 'priority', 'scheduled_date']
    search_fields = ['room__room_number', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

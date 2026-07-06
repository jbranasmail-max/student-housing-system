from django.contrib import admin
from .models import Assignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'room', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['student__name', 'room__room_number']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'

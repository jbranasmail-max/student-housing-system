from django.contrib import admin
from .models import Building, Room


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'total_floors', 'admin', 'created_at']
    search_fields = ['name', 'location']
    readonly_fields = ['created_at']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['building', 'room_number', 'apartment_number', 'floor_number', 
                    'capacity', 'current_capacity', 'price', 'is_available']
    list_filter = ['building', 'floor_number']
    search_fields = ['room_number', 'apartment_number']
    readonly_fields = ['created_at', 'is_available', 'available_beds']
    
    def is_available(self, obj):
        return "✅ متاحة" if obj.is_available else "❌ ممتلئة"
    is_available.short_description = 'الحالة'

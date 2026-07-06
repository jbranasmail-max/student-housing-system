from django.shortcuts import render
from .models import Building, Room


def building_list(request):
    """عرض قائمة المباني"""
    buildings = Building.objects.all().prefetch_related('rooms')
    context = {
        'buildings': buildings,
        'total_buildings': buildings.count(),
    }
    return render(request, 'housing/buildings.html', context)


def room_list(request):
    """عرض قائمة الغرف"""
    rooms = Room.objects.select_related('building').all()
    context = {
        'rooms': rooms,
        'total_rooms': rooms.count(),
        'available_rooms': rooms.filter(current_capacity__lt=models.F('capacity')).count(),
        'buildings': Building.objects.all(),
    }
    return render(request, 'housing/rooms.html', context)




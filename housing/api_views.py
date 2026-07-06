from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from accounts.authz import get_user_role
from accounts.models import UserProfile
from .models import Building, Room

def building_api(request, pk=None):
    """API للمباني (CRUD operations)"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'يرجى تسجيل الدخول'}, status=401)
    role = get_user_role(request.user)

    if request.method == 'GET' and pk:
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF, UserProfile.ROLE_STUDENT}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية'}, status=403)
        building = get_object_or_404(Building, pk=pk)
        data = {
            'id': building.id,
            'name': building.name,
            'location': building.location,
            'total_floors': building.total_floors,
            'admin_name': building.admin, # assuming it's a string name or we fetch name
            'rooms_count': building.rooms.count()
        }
        return JsonResponse({'success': True, 'data': data})

    if request.method == 'POST' and pk and request.path.endswith('/delete/'):
        if role != UserProfile.ROLE_MANAGER:
            return JsonResponse({'success': False, 'message': 'الحذف متاح للمدير فقط'}, status=403)
        building = get_object_or_404(Building, pk=pk)
        building.delete()
        return JsonResponse({'success': True, 'message': 'تم حذف المبنى بنجاح'})
    
    elif request.method == 'POST':
        if role != UserProfile.ROLE_MANAGER:
            return JsonResponse({'success': False, 'message': 'إدارة المباني متاحة للمدير فقط'}, status=403)
        name = request.POST.get('name', '').strip()
        location = request.POST.get('location', '').strip()
        total_floors = request.POST.get('total_floors')
        admin = request.POST.get('admin', '').strip()

        if not name or not total_floors:
            return JsonResponse({'success': False, 'error': 'اسم المبنى وعدد الطوابق حقول مطلوبة'}, status=400)

        duplicate_name = Building.objects.filter(name=name)
        if pk:
            duplicate_name = duplicate_name.exclude(pk=pk)
        if duplicate_name.exists():
            return JsonResponse({'success': False, 'error': 'اسم المبنى موجود مسبقًا'}, status=400)

        if pk:
            building = get_object_or_404(Building, pk=pk)
            building.name = name
            building.location = location
            building.total_floors = total_floors
            building.admin = admin
            try:
                building.save()
            except IntegrityError:
                return JsonResponse({'success': False, 'error': 'تعذر تحديث المبنى بسبب تعارض في البيانات'}, status=400)
            
            return JsonResponse({
                'success': True, 
                'message': 'تم تحديث المبنى بنجاح',
                'building': {
                    'id': building.id,
                    'name': building.name,
                    'location': building.location,
                    'total_floors': building.total_floors,
                    'admin_name': building.admin,
                    'rooms_count': building.rooms.count()
                }
            })
        else:
            try:
                building = Building.objects.create(
                    name=name,
                    location=location,
                    total_floors=total_floors,
                    admin=admin
                )
            except IntegrityError:
                return JsonResponse({'success': False, 'error': 'تعذر إضافة المبنى بسبب تعارض في البيانات'}, status=400)
            return JsonResponse({
                'success': True, 
                'message': 'تم إضافة المبنى بنجاح',
                'building': {
                    'id': building.id,
                    'name': building.name,
                    'location': building.location,
                    'total_floors': building.total_floors,
                    'admin_name': building.admin,
                    'rooms_count': 0
                }
            })
    
    elif request.method == 'DELETE' or (request.method == 'POST' and request.POST.get('_method') == 'DELETE'):
        if role != UserProfile.ROLE_MANAGER:
            return JsonResponse({'success': False, 'message': 'الحذف متاح للمدير فقط'}, status=403)
        building = get_object_or_404(Building, pk=pk)
        building.delete()
        return JsonResponse({'success': True, 'message': 'تم حذف المبنى بنجاح'})
    
    return JsonResponse({'success': False, 'message': 'طلب غير صالح'})

def room_api(request, pk=None):
    """API للغرف (CRUD operations)"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'يرجى تسجيل الدخول'}, status=401)
    role = get_user_role(request.user)

    if request.method == 'GET' and pk:
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF, UserProfile.ROLE_STUDENT}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية'}, status=403)
        room = get_object_or_404(Room, pk=pk)
        data = {
            'id': room.id,
            'building': room.building.id,
            'room_number': room.room_number,
            'apartment_number': room.apartment_number,
            'floor_number': room.floor_number,
            'capacity': room.capacity,
            'price': float(room.price),
        }
        return JsonResponse({'success': True, 'data': data})

    if request.method == 'POST' and pk and request.path.endswith('/delete/'):
        if role != UserProfile.ROLE_MANAGER:
            return JsonResponse({'success': False, 'message': 'الحذف متاح للمدير فقط'}, status=403)
        room = get_object_or_404(Room, pk=pk)
        room.delete()
        return JsonResponse({'success': True, 'message': 'تم حذف الغرفة بنجاح'})
    
    elif request.method == 'POST':
        if role != UserProfile.ROLE_MANAGER:
            return JsonResponse({'success': False, 'message': 'إدارة الغرف متاحة للمدير فقط'}, status=403)
        building_id = request.POST.get('building')
        room_number = request.POST.get('room_number', '').strip()
        apartment_number = request.POST.get('apartment_number', '').strip()
        floor_number = request.POST.get('floor_number')
        capacity = request.POST.get('capacity')
        price = request.POST.get('price')

        if not all([building_id, room_number, floor_number, capacity, price]):
            return JsonResponse({'success': False, 'error': 'يرجى تعبئة جميع حقول الغرفة المطلوبة'}, status=400)

        building = get_object_or_404(Building, pk=building_id)
        duplicate_room = Room.objects.filter(building=building, room_number=room_number)
        if pk:
            duplicate_room = duplicate_room.exclude(pk=pk)
        if duplicate_room.exists():
            return JsonResponse({'success': False, 'error': 'رقم الغرفة مكرر داخل نفس المبنى'}, status=400)
        
        if pk:
            room = get_object_or_404(Room, pk=pk)
            room.building = building
            room.room_number = room_number
            room.apartment_number = apartment_number
            room.floor_number = floor_number
            room.capacity = capacity
            room.price = price
            try:
                room.save()
            except IntegrityError:
                return JsonResponse({'success': False, 'error': 'تعذر تحديث الغرفة بسبب تعارض في البيانات'}, status=400)
            
            return JsonResponse({
                'success': True, 
                'message': 'تم تحديث الغرفة بنجاح',
                'room': {
                    'id': room.id,
                    'building_name': room.building.name,
                    'room_number': room.room_number,
                    'apartment_number': room.apartment_number,
                    'floor_number': room.floor_number,
                    'capacity': room.capacity,
                    'current_capacity': room.current_capacity,
                    'available_beds': room.available_beds,
                    'price': float(room.price)
                }
            })
        else:
            try:
                room = Room.objects.create(
                    building=building,
                    room_number=room_number,
                    apartment_number=apartment_number,
                    floor_number=floor_number,
                    capacity=capacity,
                    price=price
                )
            except IntegrityError:
                return JsonResponse({'success': False, 'error': 'تعذر إضافة الغرفة بسبب تعارض في البيانات'}, status=400)
            return JsonResponse({
                'success': True, 
                'message': 'تم إضافة الغرفة بنجاح',
                'room': {
                    'id': room.id,
                    'building_name': room.building.name,
                    'room_number': room.room_number,
                    'apartment_number': room.apartment_number,
                    'floor_number': room.floor_number,
                    'capacity': room.capacity,
                    'current_capacity': room.current_capacity,
                    'available_beds': room.available_beds,
                    'price': float(room.price)
                }
            })
            
    elif request.method == 'DELETE' or (request.method == 'POST' and request.POST.get('_method') == 'DELETE'):
        if role != UserProfile.ROLE_MANAGER:
            return JsonResponse({'success': False, 'message': 'الحذف متاح للمدير فقط'}, status=403)
        room = get_object_or_404(Room, pk=pk)
        room.delete()
        return JsonResponse({'success': True, 'message': 'تم حذف الغرفة بنجاح'})
    
    return JsonResponse({'success': False, 'message': 'طلب غير صالح'})

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, F
from django.utils import timezone
import json
from .models import *
from datetime import datetime, date

def index(request):
    """الصفحة الرئيسية مع جميع البيانات"""
    context = {
        # إحصائيات لوحة التحكم
        'total_students': Student.objects.count(),
        'total_buildings': Building.objects.count(),
        'total_rooms': Room.objects.count(),
        'total_payments': Payment.objects.aggregate(total=Sum('amount'))['total'] or 0,
        'available_rooms': Room.objects.filter(current_capacity__lt=F('capacity')),
        
        # الأنشطة الأخيرة
        'recent_assignments': Assignment.objects.order_by('-start_date')[:5],
        'recent_payments': Payment.objects.order_by('-payment_date')[:5],
        'recent_complaints': Complaint.objects.order_by('-created_at')[:5],
        'recent_maintenance': Maintenance.objects.order_by('-scheduled_date')[:5],
        
        # بيانات الجداول
        'students': Student.objects.all(),
        'buildings': Building.objects.all(),
        'rooms': Room.objects.select_related('building').all(),
        'assignments': Assignment.objects.select_related('student', 'room').all(),
        'payments': Payment.objects.select_related('student', 'method').all(),
        'complaints': Complaint.objects.select_related('student', 'staff').all(),
        'maintenance_requests': Maintenance.objects.select_related('room', 'staff').all(),
        
        # بيانات للنماذج
        'staff_members': Staff.objects.all(),
        'payment_methods': PaymentMethod.objects.all(),
    }
    return render(request, 'pages/index.html', context)

# ===== وظائف مساعدة =====

def validate_date(date_str):
    """تحويل وتحقق من التاريخ"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
    except (ValueError, TypeError):
        raise ValueError('تاريخ غير صحيح')

def handle_api_response(success, data=None, error=None):
    """تنسيق استجابة API"""
    response = {'success': success}
    if data:
        response.update(data)
    if error:
        response['error'] = error
    return JsonResponse(response)

# ===== API Views العامة =====

@csrf_exempt
@require_http_methods(["GET", "POST"])
def model_api(request, model_name, obj_id=None):
    """API عام للتعامل مع جميع النماذج"""
    
    models = {
        'students': Student,
        'buildings': Building,
        'rooms': Room,
        'assignments': Assignment,
        'payments': Payment,
        'complaints': Complaint,
        'maintenance': Maintenance,
    }
    
    model = models.get(model_name)
    if not model:
        return handle_api_response(False, error='نموذج غير معروف')
    
    # GET - جلب بيانات
    if request.method == 'GET' and obj_id:
        obj = get_object_or_404(model, id=obj_id)
        return handle_api_response(True, {model_name[:-1]: obj_to_dict(obj)})
    
    # POST - إضافة/تحديث/حذف
    if request.method == 'POST':
        # حذف
        if obj_id and 'delete' in request.path:
            obj = get_object_or_404(model, id=obj_id)
            handle_delete_dependencies(obj)
            obj.delete()
            return handle_api_response(True)
        
        # تحديث
        if obj_id and 'update' in request.path:
            obj = get_object_or_404(model, id=obj_id)
            return update_model(obj, request.POST)
        
        # إضافة جديدة
        return create_model(model, request.POST)
    
    return handle_api_response(False, error='طلب غير صالح')

def obj_to_dict(obj):
    """تحويل الكائن إلى قاموس"""
    if isinstance(obj, Student):
        return {
            'id': obj.id, 'name': obj.name, 'birth_date': obj.birth_date.strftime('%Y-%m-%d') if obj.birth_date else None,
            'gender': obj.gender, 'phone': obj.phone, 'email': obj.email, 'address': obj.address
        }
    elif isinstance(obj, Building):
        return {'id': obj.id, 'name': obj.name, 'admin': obj.admin, 'location': obj.location, 'total_floors': obj.total_floors}
    elif isinstance(obj, Room):
        return {
            'id': obj.id, 'building_id': obj.building.id, 'building_name': obj.building.name,
            'room_number': obj.room_number, 'apartment_number': obj.apartment_number,
            'floor_number': obj.floor_number, 'capacity': obj.capacity,
            'current_capacity': obj.current_capacity, 'price': str(obj.price)
        }
    elif isinstance(obj, Assignment):
        return {
            'id': obj.id, 'student_id': obj.student.id, 'student_name': obj.student.name,
            'room_id': obj.room.id, 'room_number': f"{obj.room.building.name} - {obj.room.room_number}",
            'start_date': obj.start_date.strftime('%Y-%m-%d') if obj.start_date else None,
            'end_date': obj.end_date.strftime('%Y-%m-%d') if obj.end_date else None,
            'status': obj.status
        }
    elif isinstance(obj, Payment):
        return {
            'id': obj.id, 'student_id': obj.student.id, 'student_name': obj.student.name,
            'amount': str(obj.amount), 'payment_date': obj.payment_date.strftime('%Y-%m-%d'),
            'method_id': obj.method.id, 'method_name': obj.method.method_name
        }
    elif isinstance(obj, Complaint):
        return {
            'id': obj.id, 'student_id': obj.student.id, 'student_name': obj.student.name,
            'staff_id': obj.staff.id if obj.staff else None,
            'staff_name': obj.staff.name if obj.staff else None,
            'description': obj.description, 'status': obj.status,
            'created_at': obj.created_at.strftime('%Y-%m-%d')
        }
    elif isinstance(obj, Maintenance):
        return {
            'id': obj.id, 'room_id': obj.room.id,
            'room_number': f"{obj.room.building.name} - {obj.room.room_number}",
            'staff_id': obj.staff.id if obj.staff else None,
            'staff_name': obj.staff.name if obj.staff else None,
            'description': obj.description, 'status': obj.status,
            'scheduled_date': obj.scheduled_date.strftime('%Y-%m-%d') if obj.scheduled_date else None
        }
    return {}

def create_model(model, data):
    """إنشاء كائن جديد"""
    try:
        if model == Student:
            if Student.objects.filter(phone=data.get('phone')).exists():
                return handle_api_response(False, error='رقم الهاتف مستخدم بالفعل')
            if Student.objects.filter(email=data.get('email')).exists():
                return handle_api_response(False, error='البريد الإلكتروني مستخدم بالفعل')
            
            obj = Student.objects.create(
                name=data.get('name'),
                birth_date=validate_date(data.get('birth_date')),
                gender=data.get('gender'),
                phone=data.get('phone'),
                email=data.get('email'),
                address=data.get('address', '')
            )
            
        elif model == Building:
            if Building.objects.filter(name=data.get('name')).exists():
                return handle_api_response(False, error='اسم المبنى مستخدم بالفعل')
            
            obj = Building.objects.create(
                name=data.get('name'),
                admin=data.get('admin',''),
                location=data.get('location', ''),
                total_floors=data.get('total_floors')
            )
            
        elif model == Room:
            building = get_object_or_404(Building, id=data.get('building'))
            if Room.objects.filter(building=building, room_number=data.get('room_number')).exists():
                return handle_api_response(False, error='رقم الغرفة موجود بالفعل في هذا المبنى')
            
            obj = Room.objects.create(
                building=building,
                room_number=data.get('room_number'),
                apartment_number=data.get('apartment_number', ''),
                floor_number=data.get('floor_number', 0),
                capacity=data.get('capacity'),
                price=data.get('price')
            )
            
        elif model == Assignment:
            student = get_object_or_404(Student, id=data.get('student'))
            room = get_object_or_404(Room, id=data.get('room'))
            start_date = validate_date(data.get('start_date'))
            
            if Assignment.objects.filter(student=student, room=room, start_date=start_date).exists():
                return handle_api_response(False, error='حجز موجود بالفعل')
            
            if room.current_capacity >= room.capacity:
                return handle_api_response(False, error='الغرفة ممتلئة')
            
            obj = Assignment.objects.create(
                student=student,
                room=room,
                start_date=start_date,
                end_date=validate_date(data.get('end_date')),
                status=data.get('status')
            )
            
            if obj.status == 'Active':
                room.current_capacity += 1
                room.save()
                
        elif model == Payment:
            student = get_object_or_404(Student, id=data.get('student'))
            method = get_object_or_404(PaymentMethod, id=data.get('method'))
            
            obj = Payment.objects.create(
                student=student,
                amount=data.get('amount'),
                payment_date=validate_date(data.get('payment_date')),
                method=method
            )
            
        elif model == Complaint:
            student = get_object_or_404(Student, id=data.get('student'))
            staff = Staff.objects.filter(id=data.get('staff')).first()
            
            obj = Complaint.objects.create(
                student=student,
                staff=staff,
                description=data.get('description'),
                status=data.get('status')
            )
            
        elif model == Maintenance:
            room = get_object_or_404(Room, id=data.get('room'))
            staff = Staff.objects.filter(id=data.get('staff')).first()
            
            obj = Maintenance.objects.create(
                room=room,
                staff=staff,
                description=data.get('description'),
                status=data.get('status'),
                scheduled_date=validate_date(data.get('scheduled_date'))
            )
        
        return handle_api_response(True, {model.__name__.lower(): obj_to_dict(obj)})
    
    except Exception as e:
        return handle_api_response(False, error=str(e))

def update_model(obj, data):
    """تحديث كائن موجود"""
    try:
        if isinstance(obj, Student):
            if Student.objects.filter(phone=data.get('phone')).exclude(id=obj.id).exists():
                return handle_api_response(False, error='رقم الهاتف مستخدم بالفعل')
            if Student.objects.filter(email=data.get('email')).exclude(id=obj.id).exists():
                return handle_api_response(False, error='البريد الإلكتروني مستخدم بالفعل')
            
            obj.name = data.get('name', obj.name)
            obj.birth_date = validate_date(data.get('birth_date')) or obj.birth_date
            obj.gender = data.get('gender', obj.gender)
            obj.phone = data.get('phone', obj.phone)
            obj.email = data.get('email', obj.email)
            obj.address = data.get('address', obj.address)
            
        elif isinstance(obj, Building):
            if Building.objects.filter(name=data.get('name')).exclude(id=obj.id).exists():
                return handle_api_response(False, error='اسم المبنى مستخدم بالفعل')
            
            obj.name = data.get('name', obj.name)
            obj.admin = data.get('admin', obj.admin )
            obj.location = data.get('location', obj.location)
            obj.total_floors = data.get('total_floors', obj.total_floors)
            
        elif isinstance(obj, Room):
            building_id = data.get('building', obj.building_id)
            room_number = data.get('room_number', obj.room_number)
            
            if Room.objects.filter(building_id=building_id, room_number=room_number).exclude(id=obj.id).exists():
                return handle_api_response(False, error='رقم الغرفة موجود بالفعل في هذا المبنى')
            
            obj.building_id = building_id
            obj.room_number = room_number
            obj.apartment_number = data.get('apartment_number', obj.apartment_number)
            obj.floor_number = data.get('floor_number', obj.floor_number)
            obj.capacity = data.get('capacity', obj.capacity)
            obj.price = data.get('price', obj.price)
            
        elif isinstance(obj, Assignment):
            old_status = obj.status
            old_room = obj.room
            
            student = get_object_or_404(Student, id=data.get('student'))
            room = get_object_or_404(Room, id=data.get('room'))
            start_date = validate_date(data.get('start_date'))
            
            if Assignment.objects.filter(student=student, room=room, start_date=start_date).exclude(id=obj.id).exists():
                return handle_api_response(False, error='حجز موجود بالفعل')
            
            obj.student = student
            obj.room = room
            obj.start_date = start_date
            obj.end_date = validate_date(data.get('end_date'))
            obj.status = data.get('status')
            
            # تحديث سعة الغرف
            if old_status == 'Active' and obj.status != 'Active':
                old_room.current_capacity = max(0, old_room.current_capacity - 1)
                old_room.save()
            elif old_status != 'Active' and obj.status == 'Active':
                room.current_capacity = min(room.capacity, room.current_capacity + 1)
                room.save()
            elif old_status == 'Active' and obj.status == 'Active' and old_room != room:
                old_room.current_capacity = max(0, old_room.current_capacity - 1)
                old_room.save()
                room.current_capacity = min(room.capacity, room.current_capacity + 1)
                room.save()
                
        elif isinstance(obj, Payment):
            obj.student_id = data.get('student', obj.student_id)
            obj.amount = data.get('amount', obj.amount)
            obj.payment_date = validate_date(data.get('payment_date')) or obj.payment_date
            obj.method_id = data.get('method', obj.method_id)
            
        elif isinstance(obj, Complaint):
            obj.student_id = data.get('student', obj.student_id)
            obj.staff_id = data.get('staff') or None
            obj.description = data.get('description', obj.description)
            obj.status = data.get('status', obj.status)
            
        elif isinstance(obj, Maintenance):
            obj.room_id = data.get('room', obj.room_id)
            obj.staff_id = data.get('staff') or None
            obj.description = data.get('description', obj.description)
            obj.status = data.get('status', obj.status)
            obj.scheduled_date = validate_date(data.get('scheduled_date'))
        
        obj.save()
        return handle_api_response(True, {obj.__class__.__name__.lower(): obj_to_dict(obj)})
    
    except Exception as e:
        return handle_api_response(False, error=str(e))

def handle_delete_dependencies(obj):
    """معالجة التبعيات عند الحذف"""
    if isinstance(obj, Student):
        Assignment.objects.filter(student=obj).delete()
        Payment.objects.filter(student=obj).delete()
        Complaint.objects.filter(student=obj).delete()
    elif isinstance(obj, Building):
        Room.objects.filter(building=obj).delete()
    elif isinstance(obj, Room):
        Assignment.objects.filter(room=obj).delete()
        Maintenance.objects.filter(room=obj).delete()

@csrf_exempt
def dashboard_stats_api(request):
    """API لإحصائيات لوحة التحكم"""
    if request.method == 'GET':
        return handle_api_response(True, {
            'total_students': Student.objects.count(),
            'total_buildings': Building.objects.count(),
            'total_rooms': Room.objects.count(),
            'total_payments': str(Payment.objects.aggregate(total=Sum('amount'))['total'] or 0)
        })
    return handle_api_response(False, error='طريقة غير مدعومة')
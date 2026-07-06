from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from .models import (
    Student, Building, Room, Assignment, Payment, 
    Complaint, Maintenance, Staff, PaymentMethod
)
import json

@csrf_exempt
@require_http_methods(["GET", "POST"])
def students_api(request):
    if request.method == 'GET':
        students = Student.objects.all().values()
        return JsonResponse({'success': True, 'students': list(students)})
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            student = Student.objects.create(
                name=data['name'],
                birth_date=data['birth_date'],
                gender=data['gender'],
                phone=data['phone'],
                email=data['email'],
                address=data.get('address', '')
            )
            return JsonResponse({'success': True, 'student_id': student.id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def student_detail_api(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
    except ObjectDoesNotExist:
        return JsonResponse({'success': False, 'message': 'الطالب غير موجود'}, status=404)
    
    if request.method == 'GET':
        student_data = {
            'id': student.id,
            'name': student.name,
            'birth_date': student.birth_date.strftime('%Y-%m-%d'),
            'gender': student.gender,
            'phone': student.phone,
            'email': student.email,
            'address': student.address
        }
        return JsonResponse({'success': True, 'student': student_data})
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            student.name = data.get('name', student.name)
            student.birth_date = data.get('birth_date', student.birth_date)
            student.gender = data.get('gender', student.gender)
            student.phone = data.get('phone', student.phone)
            student.email = data.get('email', student.email)
            student.address = data.get('address', student.address)
            student.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    elif request.method == 'DELETE':
        student.delete()
        return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def buildings_api(request):
    if request.method == 'GET':
        buildings = Building.objects.all().values()
        return JsonResponse({'success': True, 'buildings': list(buildings)})
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            building = Building.objects.create(
                name=data['name'],
                location=data.get('location', ''),
                total_floors=data['total_floors']
            )
            return JsonResponse({'success': True, 'building_id': building.id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def building_detail_api(request, building_id):
    try:
        building = Building.objects.get(id=building_id)
    except ObjectDoesNotExist:
        return JsonResponse({'success': False, 'message': 'المبنى غير موجود'}, status=404)
    
    if request.method == 'GET':
        building_data = {
            'id': building.id,
            'name': building.name,
            'location': building.location,
            'total_floors': building.total_floors
        }
        return JsonResponse({'success': True, 'building': building_data})
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            building.name = data.get('name', building.name)
            building.location = data.get('location', building.location)
            building.total_floors = data.get('total_floors', building.total_floors)
            building.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    elif request.method == 'DELETE':
        building.delete()
        return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def rooms_api(request):
    if request.method == 'GET':
        rooms = Room.objects.all().values('id', 'building__name', 'room_number', 'apartment_number', 'floor_number', 'capacity', 'current_capacity', 'price')
        return JsonResponse({'success': True, 'rooms': list(rooms)})
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            building = Building.objects.get(id=data['building'])
            room = Room.objects.create(
                building=building,
                room_number=data['room_number'],
                apartment_number=data.get('apartment_number', ''),
                floor_number=data.get('floor_number', 0),
                capacity=data['capacity'],
                current_capacity=0,
                price=data['price']
            )
            return JsonResponse({'success': True, 'room_id': room.id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def room_detail_api(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
    except ObjectDoesNotExist:
        return JsonResponse({'success': False, 'message': 'الغرفة غير موجودة'}, status=404)
    
    if request.method == 'GET':
        room_data = {
            'id': room.id,
            'building': room.building.id,
            'room_number': room.room_number,
            'apartment_number': room.apartment_number,
            'floor_number': room.floor_number,
            'capacity': room.capacity,
            'current_capacity': room.current_capacity,
            'price': str(room.price)
        }
        return JsonResponse({'success': True, 'room': room_data})
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            if 'building' in data:
                room.building = Building.objects.get(id=data['building'])
            room.room_number = data.get('room_number', room.room_number)
            room.apartment_number = data.get('apartment_number', room.apartment_number)
            room.floor_number = data.get('floor_number', room.floor_number)
            room.capacity = data.get('capacity', room.capacity)
            room.price = data.get('price', room.price)
            room.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    elif request.method == 'DELETE':
        room.delete()
        return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def assignments_api(request):
    if request.method == 'GET':
        assignments = Assignment.objects.all().values('id', 'student__name', 'room__building__name', 'room__room_number', 'start_date', 'end_date', 'status')
        return JsonResponse({'success': True, 'assignments': list(assignments)})
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            student = Student.objects.get(id=data['student'])
            room = Room.objects.get(id=data['room'])
            assignment = Assignment.objects.create(
                student=student,
                room=room,
                start_date=data['start_date'],
                end_date=data.get('end_date', None),
                status=data['status']
            )
            return JsonResponse({'success': True, 'assignment_id': assignment.id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def assignment_detail_api(request, assignment_id):
    try:
        assignment = Assignment.objects.get(id=assignment_id)
    except ObjectDoesNotExist:
        return JsonResponse({'success': False, 'message': 'الحجز غير موجود'}, status=404)
    
    if request.method == 'GET':
        assignment_data = {
            'id': assignment.id,
            'student': assignment.student.id,
            'room': assignment.room.id,
            'start_date': assignment.start_date.strftime('%Y-%m-%d'),
            'end_date': assignment.end_date.strftime('%Y-%m-%d') if assignment.end_date else None,
            'status': assignment.status
        }
        return JsonResponse({'success': True, 'assignment': assignment_data})
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            if 'student' in data:
                assignment.student = Student.objects.get(id=data['student'])
            if 'room' in data:
                assignment.room = Room.objects.get(id=data['room'])
            assignment.start_date = data.get('start_date', assignment.start_date)
            assignment.end_date = data.get('end_date', assignment.end_date)
            assignment.status = data.get('status', assignment.status)
            assignment.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    elif request.method == 'DELETE':
        assignment.delete()
        return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def payments_api(request):
    if request.method == 'GET':
        payments = Payment.objects.all().values('id', 'student__name', 'amount', 'payment_date', 'method__method_name')
        return JsonResponse({'success': True, 'payments': list(payments)})
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            student = Student.objects.get(id=data['student'])
            method = PaymentMethod.objects.get(id=data['method'])
            payment = Payment.objects.create(
                student=student,
                amount=data['amount'],
                payment_date=data['payment_date'],
                method=method
            )
            return JsonResponse({'success': True, 'payment_id': payment.id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def payment_detail_api(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
    except ObjectDoesNotExist:
        return JsonResponse({'success': False, 'message': 'الدفعة غير موجودة'}, status=404)
    
    if request.method == 'GET':
        payment_data = {
            'id': payment.id,
            'student': payment.student.id,
            'amount': str(payment.amount),
            'payment_date': payment.payment_date.strftime('%Y-%m-%d'),
            'method': payment.method.id
        }
        return JsonResponse({'success': True, 'payment': payment_data})
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            if 'student' in data:
                payment.student = Student.objects.get(id=data['student'])
            payment.amount = data.get('amount', payment.amount)
            payment.payment_date = data.get('payment_date', payment.payment_date)
            if 'method' in data:
                payment.method = PaymentMethod.objects.get(id=data['method'])
            payment.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    elif request.method == 'DELETE':
        payment.delete()
        return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def complaints_api(request):
    if request.method == 'GET':
        complaints = Complaint.objects.all().values('id', 'student__name', 'staff__name', 'description', 'status', 'created_at')
        return JsonResponse({'success': True, 'complaints': list(complaints)})
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            student = Student.objects.get(id=data['student'])
            staff = Staff.objects.get(id=data['staff']) if data.get('staff') else None
            complaint = Complaint.objects.create(
                student=student,
                staff=staff,
                description=data['description'],
                status=data['status']
            )
            return JsonResponse({'success': True, 'complaint_id': complaint.id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def complaint_detail_api(request, complaint_id):
    try:
        complaint = Complaint.objects.get(id=complaint_id)
    except ObjectDoesNotExist:
        return JsonResponse({'success': False, 'message': 'الشكوى غير موجودة'}, status=404)
    
    if request.method == 'GET':
        complaint_data = {
            'id': complaint.id,
            'student': complaint.student.id,
            'staff': complaint.staff.id if complaint.staff else None,
            'description': complaint.description,
            'status': complaint.status
        }
        return JsonResponse({'success': True, 'complaint': complaint_data})
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            if 'student' in data:
                complaint.student = Student.objects.get(id=data['student'])
            if 'staff' in data:
                complaint.staff = Staff.objects.get(id=data['staff']) if data['staff'] else None
            complaint.description = data.get('description', complaint.description)
            complaint.status = data.get('status', complaint.status)
            complaint.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    elif request.method == 'DELETE':
        complaint.delete()
        return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def maintenance_api(request):
    if request.method == 'GET':
        maintenance_requests = Maintenance.objects.all().values('id', 'room__building__name', 'room__room_number', 'staff__name', 'description', 'status', 'scheduled_date')
        return JsonResponse({'success': True, 'maintenance_requests': list(maintenance_requests)})
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            room = Room.objects.get(id=data['room'])
            staff = Staff.objects.get(id=data['staff']) if data.get('staff') else None
            maintenance = Maintenance.objects.create(
                room=room,
                staff=staff,
                description=data['description'],
                status=data['status'],
                scheduled_date=data.get('scheduled_date', None)
            )
            return JsonResponse({'success': True, 'maintenance_id': maintenance.id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def maintenance_detail_api(request, maintenance_id):
    try:
        maintenance = Maintenance.objects.get(id=maintenance_id)
    except ObjectDoesNotExist:
        return JsonResponse({'success': False, 'message': 'طلب الصيانة غير موجود'}, status=404)
    
    if request.method == 'GET':
        maintenance_data = {
            'id': maintenance.id,
            'room': maintenance.room.id,
            'staff': maintenance.staff.id if maintenance.staff else None,
            'description': maintenance.description,
            'status': maintenance.status,
            'scheduled_date': maintenance.scheduled_date.strftime('%Y-%m-%d') if maintenance.scheduled_date else None
        }
        return JsonResponse({'success': True, 'maintenance': maintenance_data})
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            if 'room' in data:
                maintenance.room = Room.objects.get(id=data['room'])
            if 'staff' in data:
                maintenance.staff = Staff.objects.get(id=data['staff']) if data['staff'] else None
            maintenance.description = data.get('description', maintenance.description)
            maintenance.status = data.get('status', maintenance.status)
            maintenance.scheduled_date = data.get('scheduled_date', maintenance.scheduled_date)
            maintenance.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    elif request.method == 'DELETE':
        maintenance.delete()
        return JsonResponse({'success': True})
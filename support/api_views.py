from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from accounts.authz import get_user_role
from accounts.models import UserProfile
from .models import Complaint, Maintenance
from students.models import Student
from staff.models import Staff
from housing.models import Room

def complaint_api(request, pk=None):
    """API للشكاوى (CRUD operations)"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'يرجى تسجيل الدخول'}, status=401)

    role = get_user_role(request.user)
    profile = getattr(request.user, "profile", None)

    if request.method == 'GET' and pk:
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF, UserProfile.ROLE_STUDENT}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية'}, status=403)
        complaint = get_object_or_404(Complaint, pk=pk)
        if role == UserProfile.ROLE_STUDENT:
            if not profile or not profile.student_id or complaint.student_id != profile.student_id:
                return JsonResponse({'success': False, 'message': 'يمكنك عرض شكاواك فقط'}, status=403)
        data = {
            'id': complaint.id,
            'student': complaint.student.id,
            'staff': complaint.staff.id if complaint.staff else '',
            'description': complaint.description,
            'status': complaint.status,
        }
        return JsonResponse({'success': True, 'data': data})

    if request.method == 'POST' and pk and request.path.endswith('/delete/'):
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية الحذف'}, status=403)
        complaint = get_object_or_404(Complaint, pk=pk)
        complaint.delete()
        return JsonResponse({'success': True, 'message': 'تم حذف الشكوى بنجاح'})
    
    elif request.method == 'POST':
        student_id = request.POST.get('student')
        staff_id = request.POST.get('staff')
        description = request.POST.get('description', '').strip()
        status = request.POST.get('status', 'Pending')

        if not description:
            return JsonResponse({'success': False, 'error': 'وصف الشكوى مطلوب'}, status=400)

        if role == UserProfile.ROLE_STUDENT:
            if not profile or not profile.student_id:
                return JsonResponse({'success': False, 'message': 'حساب الطالب غير مرتبط بسجل طالب'}, status=403)
            student = get_object_or_404(Student, pk=profile.student_id)
        elif role in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF}:
            student = get_object_or_404(Student, pk=student_id)
        else:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية'}, status=403)
        staff = get_object_or_404(Staff, pk=staff_id) if staff_id else None
        
        if pk:
            complaint = get_object_or_404(Complaint, pk=pk)
            if role == UserProfile.ROLE_STUDENT and complaint.student_id != profile.student_id:
                return JsonResponse({'success': False, 'message': 'يمكنك تعديل شكاواك فقط'}, status=403)
            complaint.student = student
            complaint.staff = staff
            complaint.description = description
            complaint.status = status
            complaint.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'تم تحديث الشكوى بنجاح',
                'complaint': {
                    'id': complaint.id,
                    'student_name': complaint.student.name,
                    'staff_name': complaint.staff.name if complaint.staff else '-',
                    'description': complaint.description[:50] + '...',
                    'status': complaint.status
                }
            })
        else:
            complaint = Complaint.objects.create(
                student=student,
                staff=staff,
                description=description,
                status=status
            )
            return JsonResponse({
                'success': True, 
                'message': 'تم إضافة الشكوى بنجاح',
                'complaint': {
                    'id': complaint.id,
                    'student_name': complaint.student.name,
                    'staff_name': complaint.staff.name if complaint.staff else '-',
                    'description': complaint.description[:50] + '...',
                    'status': complaint.status
                }
            })
            
    elif request.method == 'DELETE' or (request.method == 'POST' and request.POST.get('_method') == 'DELETE'):
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية الحذف'}, status=403)
        complaint = get_object_or_404(Complaint, pk=pk)
        complaint.delete()
        return JsonResponse({'success': True, 'message': 'تم حذف الشكوى بنجاح'})
    
    return JsonResponse({'success': False, 'message': 'طلب غير صالح'})

def maintenance_api(request, pk=None):
    """API لطلبات الصيانة (CRUD operations)"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'يرجى تسجيل الدخول'}, status=401)

    role = get_user_role(request.user)

    if request.method == 'GET' and pk:
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF, UserProfile.ROLE_STUDENT}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية'}, status=403)
        maintenance = get_object_or_404(Maintenance, pk=pk)
        data = {
            'id': maintenance.id,
            'room': maintenance.room.id,
            'staff': maintenance.staff.id if maintenance.staff else '',
            'description': maintenance.description,
            'status': maintenance.status,
            'priority': maintenance.priority,
            'scheduled_date': str(maintenance.scheduled_date) if maintenance.scheduled_date else '',
        }
        return JsonResponse({'success': True, 'data': data})

    if request.method == 'POST' and pk and request.path.endswith('/delete/'):
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية الحذف'}, status=403)
        maintenance = get_object_or_404(Maintenance, pk=pk)
        maintenance.delete()
        return JsonResponse({'success': True, 'message': 'تم حذف طلب الصيانة بنجاح'})
    
    elif request.method == 'POST':
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF, UserProfile.ROLE_STUDENT}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية'}, status=403)
        room_id = request.POST.get('room')
        staff_id = request.POST.get('staff')
        description = request.POST.get('description', '').strip()
        status = request.POST.get('status', 'Pending')
        priority = request.POST.get('priority', 'Medium')
        scheduled_date = request.POST.get('scheduled_date') or None

        if not room_id or not description:
            return JsonResponse({'success': False, 'error': 'الغرفة ووصف المشكلة حقول مطلوبة'}, status=400)
        
        room = get_object_or_404(Room, pk=room_id)
        staff = get_object_or_404(Staff, pk=staff_id) if staff_id else None
        
        if pk:
            maintenance = get_object_or_404(Maintenance, pk=pk)
            maintenance.room = room
            maintenance.staff = staff
            maintenance.description = description
            maintenance.status = status
            maintenance.priority = priority
            maintenance.scheduled_date = scheduled_date
            maintenance.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'تم تحديث طلب الصيانة بنجاح',
                'maintenance': {
                    'id': maintenance.id,
                    'room_info': str(maintenance.room),
                    'staff_name': maintenance.staff.name if maintenance.staff else '-',
                    'description': maintenance.description[:50] + '...',
                    'status': maintenance.status,
                    'priority': maintenance.priority,
                    'scheduled_date': str(maintenance.scheduled_date) if maintenance.scheduled_date else '-'
                }
            })
        else:
            maintenance = Maintenance.objects.create(
                room=room,
                staff=staff,
                description=description,
                status=status,
                priority=priority,
                scheduled_date=scheduled_date
            )
            return JsonResponse({
                'success': True, 
                'message': 'تم إضافة طلب الصيانة بنجاح',
                'maintenance': {
                    'id': maintenance.id,
                    'room_info': str(maintenance.room),
                    'staff_name': maintenance.staff.name if maintenance.staff else '-',
                    'description': maintenance.description[:50] + '...',
                    'status': maintenance.status,
                    'priority': maintenance.priority,
                    'scheduled_date': str(maintenance.scheduled_date) if maintenance.scheduled_date else '-'
                }
            })
            
    elif request.method == 'DELETE' or (request.method == 'POST' and request.POST.get('_method') == 'DELETE'):
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية الحذف'}, status=403)
        maintenance = get_object_or_404(Maintenance, pk=pk)
        maintenance.delete()
        return JsonResponse({'success': True, 'message': 'تم حذف طلب الصيانة بنجاح'})
    
    return JsonResponse({'success': False, 'message': 'طلب غير صالح'})

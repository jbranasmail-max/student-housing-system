from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from accounts.authz import get_user_role
from accounts.models import UserProfile
from .models import Assignment
from students.models import Student
from housing.models import Room

def assignment_api(request, pk=None):
    """API للحجوزات (CRUD operations)"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'يرجى تسجيل الدخول'}, status=401)

    role = get_user_role(request.user)
    profile = getattr(request.user, "profile", None)

    if request.method == 'GET' and pk:
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF, UserProfile.ROLE_STUDENT}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية'}, status=403)
        assignment = get_object_or_404(Assignment, pk=pk)
        if role == UserProfile.ROLE_STUDENT:
            if not profile or not profile.student_id or profile.student_id != assignment.student_id:
                return JsonResponse({'success': False, 'message': 'يمكنك عرض حجوزاتك فقط'}, status=403)
        data = {
            'id': assignment.id,
            'student': assignment.student.id,
            'room': assignment.room.id,
            'start_date': str(assignment.start_date),
            'end_date': str(assignment.end_date) if assignment.end_date else '',
            'status': assignment.status,
        }
        return JsonResponse({'success': True, 'data': data})

    if request.method == 'POST' and pk and request.path.endswith('/delete/'):
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية الحذف'}, status=403)
        assignment = get_object_or_404(Assignment, pk=pk)
        if role == UserProfile.ROLE_STAFF and assignment.status == 'Completed':
            return JsonResponse({'success': False, 'message': 'الموظف لا يحذف الحجوزات المكتملة'}, status=403)
        room = assignment.room
        assignment.delete()
        room.current_capacity = max(0, room.current_capacity - 1)
        room.save()
        return JsonResponse({'success': True, 'message': 'تم حذف الحجز بنجاح'})
    
    elif request.method == 'POST':
        if role == UserProfile.ROLE_STUDENT:
            return JsonResponse({'success': False, 'message': 'إنشاء الحجوزات يتم عبر الإدارة'}, status=403)
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية'}, status=403)
        student_id = request.POST.get('student')
        room_id = request.POST.get('room')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date') or None
        status = request.POST.get('status', 'Active')

        if not all([student_id, room_id, start_date]):
            return JsonResponse({'success': False, 'error': 'يرجى تعبئة بيانات الحجز الأساسية'}, status=400)
        
        student = get_object_or_404(Student, pk=student_id)
        room = get_object_or_404(Room, pk=room_id)
        
        if pk:
            assignment = get_object_or_404(Assignment, pk=pk)
            # If room changed, handle capacity
            if assignment.room != room:
                # Old room decrement
                assignment.room.current_capacity = max(0, assignment.room.current_capacity - 1)
                assignment.room.save()
                # New room increment (with check)
                if room.current_capacity >= room.capacity:
                    return JsonResponse({'success': False, 'message': 'عذراً، هذه الغرفة ممتلئة'})
                room.current_capacity += 1
                room.save()
            
            assignment.student = student
            assignment.room = room
            assignment.start_date = start_date
            assignment.end_date = end_date
            assignment.status = status
            assignment.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'تم تحديث الحجز بنجاح',
                'assignment': {
                    'id': assignment.id,
                    'student_name': assignment.student.name,
                    'room_info': str(assignment.room),
                    'start_date': str(assignment.start_date),
                    'end_date': str(assignment.end_date) if assignment.end_date else '-',
                    'status': assignment.status
                }
            })
        else:
            # Check availability
            if room.current_capacity >= room.capacity:
                return JsonResponse({'success': False, 'message': 'عذراً، هذه الغرفة ممتلئة بالكامل'})
            
            assignment = Assignment.objects.create(
                student=student,
                room=room,
                start_date=start_date,
                end_date=end_date,
                status=status
            )
            # Increment capacity
            room.current_capacity += 1
            room.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'تم إضافة الحجز بنجاح',
                'assignment': {
                    'id': assignment.id,
                    'student_name': assignment.student.name,
                    'room_info': str(assignment.room),
                    'start_date': str(assignment.start_date),
                    'end_date': str(assignment.end_date) if assignment.end_date else '-',
                    'status': assignment.status
                }
            })
            
    elif request.method == 'DELETE' or (request.method == 'POST' and request.POST.get('_method') == 'DELETE'):
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية الحذف'}, status=403)
        assignment = get_object_or_404(Assignment, pk=pk)
        room = assignment.room
        assignment.delete()
        
        # Decrement capacity
        room.current_capacity = max(0, room.current_capacity - 1)
        room.save()
        
        return JsonResponse({'success': True, 'message': 'تم حذف الحجز بنجاح'})
    
    return JsonResponse({'success': False, 'message': 'طلب غير صالح'})

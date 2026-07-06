from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import IntegrityError
from accounts.authz import get_user_role
from accounts.models import UserProfile
from .models import Student


def student_list(request):
    """عرض قائمة الطلاب"""
    students = Student.objects.all().order_by('-created_at')
    context = {
        'students': students,
        'total_students': students.count(),
    }
    return render(request, 'students/list.html', context)


def student_detail(request, pk):
    """عرض تفاصيل طالب معين"""
    student = get_object_or_404(Student, pk=pk)
    context = {
        'student': student,
        'assignments': student.assignments.all(),
        'payments': student.payments.all(),
        'complaints': student.complaints.all(),
    }
    return render(request, 'students/detail.html', context)


def student_api(request, pk=None):
    """API للطلاب (CRUD operations)"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'يرجى تسجيل الدخول'}, status=401)

    role = get_user_role(request.user)
    profile = getattr(request.user, "profile", None)

    if request.method == 'GET' and pk:
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF, UserProfile.ROLE_STUDENT}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية'}, status=403)
        student = get_object_or_404(Student, pk=pk)
        if role == UserProfile.ROLE_STUDENT:
            if not profile or not profile.student_id or profile.student_id != student.id:
                return JsonResponse({'success': False, 'message': 'لا تملك صلاحية عرض هذا السجل'}, status=403)

        data = {
            'id': student.id,
            'name': student.name,
            'birth_date': str(student.birth_date),
            'gender': student.gender,
            'phone': student.phone,
            'email': student.email,
            'address': student.address,
        }
        return JsonResponse({'success': True, 'data': data})

    if request.method == 'POST' and pk and request.path.endswith('/delete/'):
        if role != UserProfile.ROLE_MANAGER:
            return JsonResponse({'success': False, 'message': 'الحذف متاح للمدير فقط'}, status=403)
        student = get_object_or_404(Student, pk=pk)
        student.delete()
        return JsonResponse({'success': True, 'message': 'تم الحذف بنجاح'})
    
    elif request.method == 'POST':
        if role == UserProfile.ROLE_STAFF:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية تعديل بيانات الطلاب'}, status=403)
        if role == UserProfile.ROLE_STUDENT and pk and (not profile or profile.student_id != pk):
            return JsonResponse({'success': False, 'message': 'يمكنك تعديل ملفك فقط'}, status=403)
        if role == UserProfile.ROLE_STUDENT and not pk:
            return JsonResponse({'success': False, 'message': 'لا يمكنك إنشاء حساب طالب من هذه الواجهة'}, status=403)

        name = request.POST.get('name', '').strip()
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()

        if not all([name, birth_date, gender, phone, email]):
            return JsonResponse({'success': False, 'error': 'يرجى تعبئة جميع الحقول المطلوبة'}, status=400)

        duplicate_phone = Student.objects.filter(phone=phone)
        duplicate_email = Student.objects.filter(email=email)
        if pk:
            duplicate_phone = duplicate_phone.exclude(pk=pk)
            duplicate_email = duplicate_email.exclude(pk=pk)

        if duplicate_phone.exists():
            return JsonResponse({'success': False, 'error': 'رقم الهاتف مستخدم مسبقًا'}, status=400)
        if duplicate_email.exists():
            return JsonResponse({'success': False, 'error': 'البريد الإلكتروني مستخدم مسبقًا'}, status=400)

        if pk:
            student = get_object_or_404(Student, pk=pk)
            student.name = name
            student.birth_date = birth_date
            student.gender = gender
            student.phone = phone
            student.email = email
            student.address = address
            try:
                student.save()
            except IntegrityError:
                return JsonResponse({'success': False, 'error': 'تعذر تحديث الطالب بسبب تعارض في البيانات'}, status=400)
            return JsonResponse({
                'success': True, 
                'message': 'تم التحديث بنجاح',
                'student': {
                    'id': student.id,
                    'name': student.name,
                    'birth_date': str(student.birth_date),
                    'gender': student.gender,
                    'gender_display': student.get_gender_display(),
                    'phone': student.phone,
                    'email': student.email,
                    'address': student.address
                }
            })
        else:
            try:
                student = Student.objects.create(
                    name=name,
                    birth_date=birth_date,
                    gender=gender,
                    phone=phone,
                    email=email,
                    address=address
                )
            except IntegrityError:
                return JsonResponse({'success': False, 'error': 'تعذر إضافة الطالب بسبب تعارض في البيانات'}, status=400)
            return JsonResponse({
                'success': True, 
                'message': 'تم الإضافة بنجاح',
                'student': {
                    'id': student.id,
                    'name': student.name,
                    'birth_date': str(student.birth_date),
                    'gender': student.gender,
                    'gender_display': student.get_gender_display(),
                    'phone': student.phone,
                    'email': student.email,
                    'address': student.address
                }
            })
    
    elif request.method == 'DELETE' or (request.method == 'POST' and request.POST.get('_method') == 'DELETE'):
        if role != UserProfile.ROLE_MANAGER:
            return JsonResponse({'success': False, 'message': 'الحذف متاح للمدير فقط'}, status=403)
        student = get_object_or_404(Student, pk=pk)
        student.delete()
        return JsonResponse({'success': True, 'message': 'تم الحذف بنجاح'})
    
    return JsonResponse({'success': False, 'message': 'طلب غير صالح'})



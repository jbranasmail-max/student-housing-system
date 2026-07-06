from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from accounts.authz import get_user_role
from accounts.models import UserProfile
from .models import Payment
from students.models import Student
from core.models import PaymentMethod

def payment_api(request, pk=None):
    """API للمدفوعات (CRUD operations)"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'يرجى تسجيل الدخول'}, status=401)

    role = get_user_role(request.user)
    profile = getattr(request.user, "profile", None)

    if request.method == 'GET' and pk:
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF, UserProfile.ROLE_STUDENT}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية'}, status=403)
        payment = get_object_or_404(Payment, pk=pk)
        if role == UserProfile.ROLE_STUDENT:
            if not profile or not profile.student_id or payment.student_id != profile.student_id:
                return JsonResponse({'success': False, 'message': 'يمكنك عرض دفعاتك فقط'}, status=403)
        data = {
            'id': payment.id,
            'student': payment.student.id,
            'amount': float(payment.amount),
            'payment_date': str(payment.payment_date),
            'method': payment.method.id if payment.method else '',
        }
        return JsonResponse({'success': True, 'data': data})

    if request.method == 'POST' and pk and request.path.endswith('/delete/'):
        if role != UserProfile.ROLE_MANAGER:
            return JsonResponse({'success': False, 'message': 'الحذف متاح للمدير فقط'}, status=403)
        payment = get_object_or_404(Payment, pk=pk)
        payment.delete()
        return JsonResponse({'success': True, 'message': 'تم حذف الدفعة بنجاح'})
    
    elif request.method == 'POST':
        if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF, UserProfile.ROLE_STUDENT}:
            return JsonResponse({'success': False, 'message': 'لا تملك صلاحية'}, status=403)
        student_id = request.POST.get('student')
        method_id = request.POST.get('method')
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')

        if not amount or not payment_date:
            return JsonResponse({'success': False, 'error': 'المبلغ وتاريخ الدفع حقول مطلوبة'}, status=400)

        if role == UserProfile.ROLE_STUDENT:
            if not profile or not profile.student_id:
                return JsonResponse({'success': False, 'message': 'حساب الطالب غير مرتبط بسجل طالب'}, status=403)
            student = get_object_or_404(Student, pk=profile.student_id)
        else:
            student = get_object_or_404(Student, pk=student_id)
        method = get_object_or_404(PaymentMethod, pk=method_id) if method_id else None
        
        if pk:
            payment = get_object_or_404(Payment, pk=pk)
            if role == UserProfile.ROLE_STUDENT and payment.student_id != profile.student_id:
                return JsonResponse({'success': False, 'message': 'يمكنك تعديل دفعاتك فقط'}, status=403)
            payment.student = student
            payment.amount = amount
            payment.payment_date = payment_date
            payment.method = method
            payment.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'تم تحديث الدفعة بنجاح',
                'payment': {
                    'id': payment.id,
                    'student_name': payment.student.name,
                    'amount': float(payment.amount),
                    'payment_date': str(payment.payment_date),
                    'method_name': payment.method.method_name if payment.method else '-'
                }
            })
        else:
            payment = Payment.objects.create(
                student=student,
                amount=amount,
                payment_date=payment_date,
                method=method
            )
            return JsonResponse({
                'success': True, 
                'message': 'تم إضافة الدفعة بنجاح',
                'payment': {
                    'id': payment.id,
                    'student_name': payment.student.name,
                    'amount': float(payment.amount),
                    'payment_date': str(payment.payment_date),
                    'method_name': payment.method.method_name if payment.method else '-'
                }
            })
            
    elif request.method == 'DELETE' or (request.method == 'POST' and request.POST.get('_method') == 'DELETE'):
        if role != UserProfile.ROLE_MANAGER:
            return JsonResponse({'success': False, 'message': 'الحذف متاح للمدير فقط'}, status=403)
        payment = get_object_or_404(Payment, pk=pk)
        payment.delete()
        return JsonResponse({'success': True, 'message': 'تم حذف الدفعة بنجاح'})
    
    return JsonResponse({'success': False, 'message': 'طلب غير صالح'})

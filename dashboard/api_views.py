from django.http import JsonResponse
from students.models import Student
from housing.models import Building, Room
from payments.models import Payment
from staff.models import Staff
from django.db.models import Sum
from accounts.authz import get_user_role
from accounts.models import UserProfile

def dashboard_stats_api(request):
    """API للإحصائيات الحية في لوحة التحكم"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'يرجى تسجيل الدخول'}, status=401)

    role = get_user_role(request.user)
    if role not in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF, UserProfile.ROLE_STUDENT}:
        return JsonResponse({'success': False, 'message': 'لا تملك صلاحية'}, status=403)

    total_students = Student.objects.count()
    total_buildings = Building.objects.count()
    total_rooms = Room.objects.count()
    total_staff = Staff.objects.count()
    total_payments = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    
    return JsonResponse({
        'success': True,
        'total_students': total_students,
        'total_buildings': total_buildings,
        'total_rooms': total_rooms,
        'total_staff': total_staff,
        'total_payments': float(total_payments)
    })

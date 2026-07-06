from django.shortcuts import redirect, render
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from students.models import Student
from housing.models import Building, Room
from bookings.models import Assignment
from payments.models import Payment
from support.models import Complaint, Maintenance
from staff.models import Staff
from core.models import PaymentMethod, Role
from django.db.models import Sum, F
from accounts.authz import get_user_role
from accounts.models import UserProfile

DEFAULT_PAYMENT_METHODS = [
    "نقدي",
    "تحويل بنكي",
    "بطاقة ائتمانية",
    "محفظة إلكترونية",
]


def ensure_default_payment_methods():
    if PaymentMethod.objects.exists():
        return
    PaymentMethod.objects.bulk_create(
        [PaymentMethod(method_name=name) for name in DEFAULT_PAYMENT_METHODS],
        ignore_conflicts=True,
    )


def public_home(request):
    ensure_default_payment_methods()
    context = {
        "total_students": Student.objects.count(),
        "total_staff": Staff.objects.filter(is_active=True).count(),
        "total_buildings": Building.objects.count(),
        "total_rooms": Room.objects.count(),
        "available_rooms": Room.objects.filter(current_capacity__lt=F("capacity")).count(),
        "active_bookings": Assignment.objects.filter(status="Active").count(),
        "resolved_complaints": Complaint.objects.filter(status="Resolved").count(),
        "completed_maintenance": Maintenance.objects.filter(status="Completed").count(),
        "annual_payments_total": Payment.objects.aggregate(total=Sum("amount"))["total"] or 0,
    }
    return render(request, "landing.html", context)


@login_required
def index(request):
    """
    Single view for the entire application - All data in one place
    """
    ensure_default_payment_methods()
    role = get_user_role(request.user)
    if role is None:
        return HttpResponseForbidden("لا توجد صلاحية مخصصة لهذا الحساب")

    default_section = "dashboard"
    if role == UserProfile.ROLE_STAFF:
        default_section = "assignments"
    if role == UserProfile.ROLE_STUDENT:
        default_section = "payments"

    all_staff_members = Staff.objects.select_related('role').all()
    staff_rows = []
    for member in all_staff_members:
        profile = getattr(member, "user_profile", None)
        linked_user = profile.user if profile else None
        staff_rows.append(
            {
                "id": member.id,
                "name": member.name,
                "role_name": member.role.role_name if member.role else "-",
                "phone": member.phone or "-",
                "email": member.email or "-",
                "hire_date": member.hire_date,
                "is_active": member.is_active,
                "username": linked_user.username if linked_user else "-",
                "account_active": linked_user.is_active if linked_user else None,
            }
        )

    context = {
        'user_role': role,
        'default_section': default_section,
        # Statistics
        'total_students': Student.objects.count(),
        'total_buildings': Building.objects.count(),
        'total_rooms': Room.objects.count(),
        'total_staff': Staff.objects.count(),
        'total_payments': Payment.objects.aggregate(total=Sum('amount'))['total'] or 0,
        'available_rooms': Room.objects.filter(current_capacity__lt=F('capacity')).count(),
        'active_bookings': Assignment.objects.filter(status='Active').count(),
        'pending_complaints': Complaint.objects.filter(status='Pending').count(),
        'pending_maintenance': Maintenance.objects.filter(status='Pending').count(),
        
        # All Data for Each Section
        'students': Student.objects.all().order_by('-created_at'),
        'buildings': Building.objects.all().prefetch_related('rooms'),
        'rooms': Room.objects.select_related('building').all(),
        'assignments': Assignment.objects.select_related('student', 'room').all(),
        'payments': Payment.objects.select_related('student', 'method').order_by('-payment_date'),
        'complaints': Complaint.objects.select_related('student', 'staff').order_by('-created_at'),
        'maintenance_requests': Maintenance.objects.select_related('room', 'staff').order_by('-created_at'),
        
        # Recent Activities (for dashboard)
        'recent_assignments': Assignment.objects.select_related('student', 'room').order_by('-created_at')[:5],
        'recent_payments': Payment.objects.select_related('student', 'method').order_by('-payment_date')[:5],
        'recent_complaints': Complaint.objects.select_related('student', 'staff').order_by('-created_at')[:5],
        
        # For Dropdowns/Selects
        'staff_members': Staff.objects.filter(is_active=True),
        'all_staff_members': all_staff_members,
        'staff_rows': staff_rows,
        'staff_roles': Role.objects.all().order_by('role_name'),
        'payment_methods': PaymentMethod.objects.all(),
    }

    if role == UserProfile.ROLE_STUDENT:
        profile = getattr(request.user, "profile", None)
        student = getattr(profile, "student", None) if profile else None
        if not student:
            return HttpResponseForbidden("حساب الطالب غير مربوط بسجل طالب")

        context.update(
            {
                'students': Student.objects.filter(id=student.id),
                'assignments': Assignment.objects.select_related('student', 'room').filter(student=student),
                'payments': Payment.objects.select_related('student', 'method').filter(student=student).order_by('-payment_date'),
                'complaints': Complaint.objects.select_related('student', 'staff').filter(student=student).order_by('-created_at'),
                'recent_assignments': Assignment.objects.select_related('student', 'room').filter(student=student).order_by('-created_at')[:5],
                'recent_payments': Payment.objects.select_related('student', 'method').filter(student=student).order_by('-payment_date')[:5],
                'recent_complaints': Complaint.objects.select_related('student', 'staff').filter(student=student).order_by('-created_at')[:5],
            }
        )
    
    return render(request, 'index.html', context)

from django.shortcuts import render
from .models import Complaint, Maintenance


def complaint_list(request):
    """عرض قائمة الشكاوى"""
    complaints = Complaint.objects.select_related('student', 'staff').all()
    context = {
        'complaints': complaints,
        'pending_count': complaints.filter(status='Pending').count(),
    }
    return render(request, 'support/complaints.html', context)


def maintenance_list(request):
    """عرض قائمة الصيانة"""
    maintenance = Maintenance.objects.select_related('room', 'staff').all()
    context = {
        'maintenance_requests': maintenance,
        'pending_count': maintenance.filter(status='Pending').count(),
    }
    return render(request, 'support/maintenance.html', context)

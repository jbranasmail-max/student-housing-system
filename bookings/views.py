from django.shortcuts import render
from .models import Assignment


def booking_list(request):
    """عرض قائمة الحجوزات"""
    assignments = Assignment.objects.select_related('student', 'room').all()
    context = {
        'assignments': assignments,
        'active_assignments': assignments.filter(status='Active').count(),
    }
    return render(request, 'bookings/list.html', context)

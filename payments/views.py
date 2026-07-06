from django.shortcuts import render
from .models import Payment


def payment_list(request):
    """عرض قائمة المدفوعات"""
    payments = Payment.objects.select_related('student', 'method').all()
    context = {
        'payments': payments,
        'total_amount': sum(p.amount for p in payments),
    }
    return render(request, 'payments/list.html', context)

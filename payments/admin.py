from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'payment_date', 'method', 'created_at']
    list_filter = ['payment_date', 'method', 'created_at']
    search_fields = ['student__name', 'notes']
    readonly_fields = ['created_at']
    date_hierarchy = 'payment_date'

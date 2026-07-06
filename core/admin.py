from django.contrib import admin
from .models import Role, PaymentMethod


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['role_name']
    search_fields = ['role_name']
    
    def has_module_permission(self, request):
        return False


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['method_name']
    search_fields = ['method_name']

from django.contrib import admin
from .models import Role, PaymentMethod, Student, Building, Room, Staff, Assignment, Payment, Complaint, Maintenance

# 1. Role
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['role_name']
    search_fields = ['role_name']
    
    def has_module_permission(self, request):
        return False

# 2. PaymentMethod
@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['method_name']
    search_fields = ['method_name']

# 3. Student
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name','birth_date','gender','phone','email','address']
    list_filter = ['gender','address']
    search_fields = ['name','phone','email','address']

# 4. Building
@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['name','location','total_floors','admin']
    search_fields = ['name','location']

# 5. Room
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['building','room_number','apartment_number','floor_number','capacity','current_capacity','price']
    list_filter = ['building','floor_number']
    search_fields = ['room_number','apartment_number']

# 6. Staff
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['name','role','phone','email']
    list_filter = ['role']
    search_fields = ['name','phone','email']

# 7. Assignment
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['student','room','start_date','end_date','status']
    list_filter = ['status']
    search_fields = ['student__name','room__room_number']

# 8. Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student','amount','payment_date','method']
    list_filter = ['payment_date','method']
    search_fields = ['student__name']

# 9. Complaint
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['student','staff','status','created_at','description']
    list_filter = ['status','created_at','description']
    search_fields = ['student__name','description']


# 10. Maintenance
@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ['room','staff','status','scheduled_date']
    list_filter = ['status','scheduled_date']
    search_fields = ['room__room_number','description']




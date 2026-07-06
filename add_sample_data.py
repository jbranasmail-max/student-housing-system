#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_hospaital.settings')
django.setup()

from pages.models import (
    Student, Building, Room, Assignment, Payment, 
    Complaint, Maintenance, Staff, Role, PaymentMethod
)

def add_sample_data():
    print("إضافة بيانات تجريبية...")
    
    # إضافة الأدوار
    roles = ['مدير', 'موظف استقبال', 'فني صيانة', 'أمن']
    for role_name in roles:
        role, created = Role.objects.get_or_create(role_name=role_name)
        if created:
            print(f"تم إضافة دور: {role_name}")
    
    # إضافة طرق الدفع
    payment_methods = ['نقدي', 'بطاقة ائتمان', 'تحويل بنكي', 'شيك']
    for method_name in payment_methods:
        method, created = PaymentMethod.objects.get_or_create(method_name=method_name)
        if created:
            print(f"تم إضافة طريقة دفع: {method_name}")
    
    # إضافة الموظفين
    staff_data = [
        {'name': 'أحمد محمد', 'role': 'مدير', 'phone': '0501234567', 'email': 'ahmed@hospital.com'},
        {'name': 'فاطمة علي', 'role': 'موظف استقبال', 'phone': '0501234568', 'email': 'fatima@hospital.com'},
        {'name': 'محمد سالم', 'role': 'فني صيانة', 'phone': '0501234569', 'email': 'mohammed@hospital.com'},
    ]
    
    for staff_info in staff_data:
        role = Role.objects.get(role_name=staff_info['role'])
        staff, created = Staff.objects.get_or_create(
            name=staff_info['name'],
            defaults={
                'role': role,
                'phone': staff_info['phone'],
                'email': staff_info['email']
            }
        )
        if created:
            print(f"تم إضافة موظف: {staff_info['name']}")
    
    # إضافة الطلاب
    students_data = [
        {'name': 'علي أحمد', 'birth_date': date(2000, 5, 15), 'gender': 'M', 'phone': '0501111111', 'email': 'ali@student.com', 'address': 'الرياض'},
        {'name': 'سارة محمد', 'birth_date': date(2001, 3, 20), 'gender': 'F', 'phone': '0501111112', 'email': 'sara@student.com', 'address': 'جدة'},
        {'name': 'خالد سالم', 'birth_date': date(1999, 8, 10), 'gender': 'M', 'phone': '0501111113', 'email': 'khalid@student.com', 'address': 'الدمام'},
        {'name': 'نورا عبدالله', 'birth_date': date(2002, 1, 25), 'gender': 'F', 'phone': '0501111114', 'email': 'nora@student.com', 'address': 'مكة'},
        {'name': 'عبدالرحمن فهد', 'birth_date': date(2000, 12, 5), 'gender': 'M', 'phone': '0501111115', 'email': 'abdulrahman@student.com', 'address': 'المدينة'},
    ]
    
    for student_info in students_data:
        student, created = Student.objects.get_or_create(
            email=student_info['email'],
            defaults=student_info
        )
        if created:
            print(f"تم إضافة طالب: {student_info['name']}")
    
    # إضافة المباني
    buildings_data = [
        {'name': 'مبنى الطلاب الأول', 'location': 'الجانب الشرقي', 'total_floors': 5},
        {'name': 'مبنى الطالبات الأول', 'location': 'الجانب الغربي', 'total_floors': 4},
        {'name': 'مبنى الطلاب الثاني', 'location': 'الجانب الشمالي', 'total_floors': 6},
    ]
    
    for building_info in buildings_data:
        building, created = Building.objects.get_or_create(
            name=building_info['name'],
            defaults=building_info
        )
        if created:
            print(f"تم إضافة مبنى: {building_info['name']}")
    
    # إضافة الغرف
    buildings = Building.objects.all()
    room_counter = 1
    
    for building in buildings:
        for floor in range(1, building.total_floors + 1):
            for room_num in range(1, 6):  # 5 غرف في كل طابق
                room_number = f"{floor}{room_num:02d}"
                capacity = 2 if building.name.startswith('مبنى الطالبات') else 4
                price = Decimal('1500.00') if capacity == 2 else Decimal('1200.00')
                
                room, created = Room.objects.get_or_create(
                    building=building,
                    room_number=room_number,
                    defaults={
                        'floor_number': floor,
                        'capacity': capacity,
                        'current_capacity': 0,
                        'price': price
                    }
                )
                if created:
                    print(f"تم إضافة غرفة: {building.name} - {room_number}")
                    room_counter += 1
    
    # إضافة الحجوزات
    students = Student.objects.all()
    rooms = Room.objects.all()[:len(students)]  # نأخذ عدد غرف يساوي عدد الطلاب
    
    for i, student in enumerate(students):
        if i < len(rooms):
            room = rooms[i]
            assignment, created = Assignment.objects.get_or_create(
                student=student,
                room=room,
                start_date=date.today() - timedelta(days=30),
                defaults={
                    'end_date': date.today() + timedelta(days=335),  # سنة دراسية
                    'status': 'Active'
                }
            )
            if created:
                # تحديث السعة الحالية للغرفة
                room.current_capacity += 1
                room.save()
                print(f"تم إضافة حجز: {student.name} → {room}")
    
    # إضافة المدفوعات
    payment_method = PaymentMethod.objects.first()
    assignments = Assignment.objects.all()
    
    for assignment in assignments:
        # دفعة شهرية
        payment, created = Payment.objects.get_or_create(
            student=assignment.student,
            amount=assignment.room.price,
            payment_date=date.today() - timedelta(days=15),
            defaults={'method': payment_method}
        )
        if created:
            print(f"تم إضافة دفعة: {assignment.student.name} - {assignment.room.price}")
    
    # إضافة الشكاوى
    staff_member = Staff.objects.first()
    complaints_data = [
        {'student': students[0], 'description': 'مشكلة في التكييف', 'status': 'Pending'},
        {'student': students[1], 'description': 'انقطاع في الإنترنت', 'status': 'In Progress'},
        {'student': students[2], 'description': 'مشكلة في الإضاءة', 'status': 'Resolved'},
    ]
    
    for complaint_info in complaints_data:
        complaint, created = Complaint.objects.get_or_create(
            student=complaint_info['student'],
            description=complaint_info['description'],
            defaults={
                'staff': staff_member,
                'status': complaint_info['status']
            }
        )
        if created:
            print(f"تم إضافة شكوى: {complaint_info['description']}")
    
    # إضافة طلبات الصيانة
    maintenance_data = [
        {'room': rooms[0], 'description': 'إصلاح الحمام', 'status': 'Pending', 'scheduled_date': date.today() + timedelta(days=2)},
        {'room': rooms[1], 'description': 'صيانة التكييف', 'status': 'In Progress', 'scheduled_date': date.today() + timedelta(days=1)},
        {'room': rooms[2], 'description': 'إصلاح النافذة', 'status': 'Completed', 'scheduled_date': date.today() - timedelta(days=1)},
    ]
    
    maintenance_staff = Staff.objects.filter(role__role_name='فني صيانة').first()
    
    for maintenance_info in maintenance_data:
        maintenance, created = Maintenance.objects.get_or_create(
            room=maintenance_info['room'],
            description=maintenance_info['description'],
            defaults={
                'staff': maintenance_staff,
                'status': maintenance_info['status'],
                'scheduled_date': maintenance_info['scheduled_date']
            }
        )
        if created:
            print(f"تم إضافة طلب صيانة: {maintenance_info['description']}")
    
    print("\nتم الانتهاء من إضافة البيانات التجريبية!")
    print(f"الطلاب: {Student.objects.count()}")
    print(f"المباني: {Building.objects.count()}")
    print(f"الغرف: {Room.objects.count()}")
    print(f"الحجوزات: {Assignment.objects.count()}")
    print(f"المدفوعات: {Payment.objects.count()}")
    print(f"الشكاوى: {Complaint.objects.count()}")
    print(f"طلبات الصيانة: {Maintenance.objects.count()}")

if __name__ == '__main__':
    add_sample_data()
from django.core.management.base import BaseCommand
from pages.models import (
    Student, Building, Room, Assignment, Payment, 
    Complaint, Maintenance, Staff, Role, PaymentMethod
)
from datetime import date, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'إضافة بيانات تجريبية لنظام إدارة السكن الطلابي'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='مسح البيانات الموجودة قبل إضافة البيانات الجديدة',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('مسح البيانات الموجودة...')
            # مسح البيانات بالترتيب الصحيح لتجنب مشاكل المفاتيح الخارجية
            Maintenance.objects.all().delete()
            Complaint.objects.all().delete()
            Payment.objects.all().delete()
            Assignment.objects.all().delete()
            Room.objects.all().delete()
            Building.objects.all().delete()
            Student.objects.all().delete()
            Staff.objects.all().delete()
            Role.objects.all().delete()
            PaymentMethod.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('تم مسح البيانات الموجودة'))

        self.stdout.write('بدء إضافة البيانات التجريبية...')
        
        # إضافة الأدوار
        roles_data = ['مدير', 'موظف استقبال', 'فني صيانة', 'أمن', 'محاسب']
        for role_name in roles_data:
            role, created = Role.objects.get_or_create(role_name=role_name)
            if created:
                self.stdout.write(f'تم إضافة دور: {role_name}')
        
        # إضافة طرق الدفع
        payment_methods_data = ['نقدي', 'بطاقة ائتمان', 'تحويل بنكي', 'شيك', 'محفظة إلكترونية']
        for method_name in payment_methods_data:
            method, created = PaymentMethod.objects.get_or_create(method_name=method_name)
            if created:
                self.stdout.write(f'تم إضافة طريقة دفع: {method_name}')
        
        # إضافة الموظفين
        staff_data = [
            {'name': 'أحمد محمد العلي', 'role': 'مدير', 'phone': '0501234567', 'email': 'ahmed.manager@hospital.com'},
            {'name': 'فاطمة علي السالم', 'role': 'موظف استقبال', 'phone': '0501234568', 'email': 'fatima.reception@hospital.com'},
            {'name': 'محمد سالم الأحمد', 'role': 'فني صيانة', 'phone': '0501234569', 'email': 'mohammed.maintenance@hospital.com'},
            {'name': 'خالد عبدالله النصر', 'role': 'أمن', 'phone': '0501234570', 'email': 'khalid.security@hospital.com'},
            {'name': 'نورا حسن المطيري', 'role': 'محاسب', 'phone': '0501234571', 'email': 'nora.accounting@hospital.com'},
        ]
        
        for staff_info in staff_data:
            role = Role.objects.get(role_name=staff_info['role'])
            staff, created = Staff.objects.get_or_create(
                email=staff_info['email'],
                defaults={
                    'name': staff_info['name'],
                    'role': role,
                    'phone': staff_info['phone']
                }
            )
            if created:
                self.stdout.write(f'تم إضافة موظف: {staff_info["name"]}')
        
        # إضافة الطلاب
        students_data = [
            {'name': 'علي أحمد الزهراني', 'birth_date': date(2000, 5, 15), 'gender': 'M', 'phone': '0501111111', 'email': 'ali.alzahrani@student.com', 'address': 'الرياض، حي النخيل'},
            {'name': 'سارة محمد القحطاني', 'birth_date': date(2001, 3, 20), 'gender': 'F', 'phone': '0501111112', 'email': 'sara.alqahtani@student.com', 'address': 'جدة، حي الروضة'},
            {'name': 'خالد سالم العتيبي', 'birth_date': date(1999, 8, 10), 'gender': 'M', 'phone': '0501111113', 'email': 'khalid.alotaibi@student.com', 'address': 'الدمام، حي الفيصلية'},
            {'name': 'نورا عبدالله الشهري', 'birth_date': date(2002, 1, 25), 'gender': 'F', 'phone': '0501111114', 'email': 'nora.alshahri@student.com', 'address': 'مكة المكرمة، حي العزيزية'},
            {'name': 'عبدالرحمن فهد المالكي', 'birth_date': date(2000, 12, 5), 'gender': 'M', 'phone': '0501111115', 'email': 'abdulrahman.almalki@student.com', 'address': 'المدينة المنورة، حي قباء'},
            {'name': 'ريم سعد الغامدي', 'birth_date': date(2001, 7, 18), 'gender': 'F', 'phone': '0501111116', 'email': 'reem.alghamdi@student.com', 'address': 'الطائف، حي الشفا'},
            {'name': 'يوسف عمر الحربي', 'birth_date': date(2000, 4, 12), 'gender': 'M', 'phone': '0501111117', 'email': 'yousef.alharbi@student.com', 'address': 'بريدة، حي الإسكان'},
            {'name': 'أمل حسن العسيري', 'birth_date': date(2002, 9, 8), 'gender': 'F', 'phone': '0501111118', 'email': 'amal.alasiri@student.com', 'address': 'أبها، حي المنهل'},
        ]
        
        for student_info in students_data:
            student, created = Student.objects.get_or_create(
                email=student_info['email'],
                defaults=student_info
            )
            if created:
                self.stdout.write(f'تم إضافة طالب: {student_info["name"]}')
        
        # إضافة المباني
        buildings_data = [
            {'name': 'مبنى الطلاب الأول', 'location': 'الجانب الشرقي من الحرم الجامعي', 'total_floors': 5},
            {'name': 'مبنى الطالبات الأول', 'location': 'الجانب الغربي من الحرم الجامعي', 'total_floors': 4},
            {'name': 'مبنى الطلاب الثاني', 'location': 'الجانب الشمالي من الحرم الجامعي', 'total_floors': 6},
            {'name': 'مبنى الطالبات الثاني', 'location': 'الجانب الجنوبي من الحرم الجامعي', 'total_floors': 5},
        ]
        
        for building_info in buildings_data:
            building, created = Building.objects.get_or_create(
                name=building_info['name'],
                defaults=building_info
            )
            if created:
                self.stdout.write(f'تم إضافة مبنى: {building_info["name"]}')
        
        # إضافة الغرف
        buildings = Building.objects.all()
        rooms_created = 0
        
        for building in buildings:
            for floor in range(1, building.total_floors + 1):
                rooms_per_floor = 8 if 'طالبات' in building.name else 10
                for room_num in range(1, rooms_per_floor + 1):
                    room_number = f"{floor}{room_num:02d}"
                    
                    # تحديد السعة والسعر حسب نوع المبنى
                    if 'طالبات' in building.name:
                        capacity = 2
                        price = Decimal('1800.00')
                    else:
                        capacity = 4
                        price = Decimal('1400.00')
                    
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
                        rooms_created += 1
        
        self.stdout.write(f'تم إضافة {rooms_created} غرفة')
        
        # إضافة الحجوزات
        students = Student.objects.all()
        available_rooms = Room.objects.filter(current_capacity=0)[:len(students)]
        assignments_created = 0
        
        for i, student in enumerate(students):
            if i < len(available_rooms):
                room = available_rooms[i]
                assignment, created = Assignment.objects.get_or_create(
                    student=student,
                    room=room,
                    start_date=date.today() - timedelta(days=60),
                    defaults={
                        'end_date': date.today() + timedelta(days=305),
                        'status': 'Active'
                    }
                )
                if created:
                    # تحديث السعة الحالية للغرفة
                    room.current_capacity += 1
                    room.save()
                    assignments_created += 1
        
        self.stdout.write(f'تم إضافة {assignments_created} حجز')
        
        # إضافة المدفوعات
        payment_methods = PaymentMethod.objects.all()
        assignments = Assignment.objects.all()
        payments_created = 0
        
        for assignment in assignments:
            # إضافة عدة دفعات لكل طالب
            for month_offset in [0, 30, 60]:
                payment_date = date.today() - timedelta(days=month_offset)
                payment, created = Payment.objects.get_or_create(
                    student=assignment.student,
                    payment_date=payment_date,
                    defaults={
                        'amount': assignment.room.price,
                        'method': payment_methods[month_offset % len(payment_methods)]
                    }
                )
                if created:
                    payments_created += 1
        
        self.stdout.write(f'تم إضافة {payments_created} دفعة')
        
        # إضافة الشكاوى
        staff_members = Staff.objects.all()
        complaints_data = [
            {'student': students[0], 'description': 'مشكلة في نظام التكييف - لا يعمل بشكل صحيح', 'status': 'Pending'},
            {'student': students[1], 'description': 'انقطاع متكرر في خدمة الإنترنت', 'status': 'In Progress'},
            {'student': students[2], 'description': 'مشكلة في الإضاءة - المصباح لا يعمل', 'status': 'Resolved'},
            {'student': students[3], 'description': 'تسريب في الحمام', 'status': 'Pending'},
            {'student': students[4], 'description': 'ضوضاء من الغرفة المجاورة', 'status': 'In Progress'},
        ]
        
        complaints_created = 0
        for complaint_info in complaints_data:
            if len(students) > complaints_created:
                complaint, created = Complaint.objects.get_or_create(
                    student=complaint_info['student'],
                    description=complaint_info['description'],
                    defaults={
                        'staff': staff_members[complaints_created % len(staff_members)],
                        'status': complaint_info['status']
                    }
                )
                if created:
                    complaints_created += 1
        
        self.stdout.write(f'تم إضافة {complaints_created} شكوى')
        
        # إضافة طلبات الصيانة
        maintenance_staff = Staff.objects.filter(role__role_name='فني صيانة').first()
        occupied_rooms = Room.objects.filter(current_capacity__gt=0)[:5]
        maintenance_data = [
            {'description': 'إصلاح صنبور الحمام', 'status': 'Pending', 'days_offset': 3},
            {'description': 'صيانة دورية لنظام التكييف', 'status': 'In Progress', 'days_offset': 1},
            {'description': 'إصلاح النافذة المكسورة', 'status': 'Completed', 'days_offset': -2},
            {'description': 'تنظيف مجاري التهوية', 'status': 'Pending', 'days_offset': 5},
            {'description': 'إصلاح قفل الباب', 'status': 'In Progress', 'days_offset': 0},
        ]
        
        maintenance_created = 0
        for i, maintenance_info in enumerate(maintenance_data):
            if i < len(occupied_rooms):
                room = occupied_rooms[i]
                scheduled_date = date.today() + timedelta(days=maintenance_info['days_offset'])
                
                maintenance, created = Maintenance.objects.get_or_create(
                    room=room,
                    description=maintenance_info['description'],
                    defaults={
                        'staff': maintenance_staff,
                        'status': maintenance_info['status'],
                        'scheduled_date': scheduled_date
                    }
                )
                if created:
                    maintenance_created += 1
        
        self.stdout.write(f'تم إضافة {maintenance_created} طلب صيانة')
        
        # عرض الإحصائيات النهائية
        self.stdout.write(self.style.SUCCESS('\n=== تم الانتهاء من إضافة البيانات التجريبية ==='))
        self.stdout.write(f'الطلاب: {Student.objects.count()}')
        self.stdout.write(f'المباني: {Building.objects.count()}')
        self.stdout.write(f'الغرف: {Room.objects.count()}')
        self.stdout.write(f'الحجوزات: {Assignment.objects.count()}')
        self.stdout.write(f'المدفوعات: {Payment.objects.count()}')
        self.stdout.write(f'الشكاوى: {Complaint.objects.count()}')
        self.stdout.write(f'طلبات الصيانة: {Maintenance.objects.count()}')
        self.stdout.write(f'الموظفين: {Staff.objects.count()}')
        self.stdout.write(f'الأدوار: {Role.objects.count()}')
        self.stdout.write(f'طرق الدفع: {PaymentMethod.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('\nيمكنك الآن زيارة الموقع لرؤية البيانات!'))
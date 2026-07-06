from django.db import models

# 1. Roles

class Role(models.Model):
    role_name = models.CharField(verbose_name='العمل الوظيفي', max_length=50, unique=True)

    def __str__(self):
        return self.role_name
    
    class Meta:
        verbose_name = "العمل الوظيفي"
        verbose_name_plural = "الأعمال الوظيفية"
    
    

# 2. PaymentMethods
class PaymentMethod(models.Model):
    method_name = models.CharField(verbose_name='طريقة الدفع', max_length=50, unique=True)

    def __str__(self):
        return self.method_name

    class Meta:
        verbose_name = "طريقة الدفع"
        verbose_name_plural = "طرق الدفع"

# 3. Students
class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'ذكر'),
        ('F', 'أنثى'),
    ]
    name = models.CharField(verbose_name='الاسم', max_length=100)
    birth_date = models.DateField(verbose_name='تاريخ الميلاد')
    gender = models.CharField(verbose_name='الجنس', max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(verbose_name='رقم الهاتف', max_length=15, unique=True)
    email = models.EmailField(verbose_name='البريد الإلكتروني', unique=True)
    address = models.CharField(verbose_name='العنوان', max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "طالب"
        verbose_name_plural = "الطلاب"

# 4. Buildings
class Building(models.Model):
    name = models.CharField(verbose_name='اسم المبنى', max_length=100, unique=True)
    location = models.CharField(verbose_name='الموقع', max_length=255, blank=True, null=True)
    total_floors = models.PositiveIntegerField(verbose_name='عدد الطوابق')
    admin = models.CharField(verbose_name='المسؤول',max_length=100 ,blank=True ,null=True )
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "مبنى"
        verbose_name_plural = "المباني"

# 5. Rooms
class Room(models.Model):
    building = models.ForeignKey(Building, verbose_name='المبنى', on_delete=models.CASCADE)
    room_number = models.CharField(verbose_name='رقم الغرفة', max_length=10)
    apartment_number = models.CharField(verbose_name='رقم الشقة', max_length=10, blank=True, null=True)
    floor_number = models.IntegerField(verbose_name='الطابق')
    capacity = models.PositiveIntegerField(verbose_name='السعة')
    current_capacity = models.PositiveIntegerField(verbose_name='السعة الحالية', default=0)
    price = models.DecimalField(verbose_name='السعر', max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('building', 'room_number')
        verbose_name = "غرفة"
        verbose_name_plural = "الغرف"

    def __str__(self):
        return f"{self.building.name} - {self.room_number}"

# 6. Staff
class Staff(models.Model):
    name = models.CharField(verbose_name='الاسم', max_length=100)
    role = models.ForeignKey(Role, verbose_name='الوظيفة', on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(verbose_name='رقم الهاتف', max_length=15, unique=True, blank=True, null=True)
    email = models.EmailField(verbose_name='البريد الإلكتروني', unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "موظف"
        verbose_name_plural = "الموظفين"

# 7. Assignments
class Assignment(models.Model):
    STATUS_CHOICES = [
        ('Active', 'نشطة'),
        ('Completed', 'مكتملة'),
        ('Cancelled', 'ملغاة'),
    ]
    student = models.ForeignKey(Student, verbose_name='الطالب', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, verbose_name='الغرفة', on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name='تاريخ البداية')
    end_date = models.DateField(verbose_name='تاريخ النهاية', blank=True, null=True)
    status = models.CharField(verbose_name='الحالة', max_length=20, choices=STATUS_CHOICES, default='Active')

    class Meta:
        unique_together = ('student', 'room', 'start_date')
        verbose_name = "حجز"
        verbose_name_plural = "الحجوزات"

    def __str__(self):
        return f"{self.student.name} → {self.room}"

# 8. Payments
class Payment(models.Model):
    student = models.ForeignKey(Student, verbose_name='الطالب', on_delete=models.CASCADE)
    amount = models.DecimalField(verbose_name='المبلغ', max_digits=10, decimal_places=2)
    payment_date = models.DateField(verbose_name='تاريخ الدفع')
    method = models.ForeignKey(PaymentMethod, verbose_name='طريقة الدفع', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.amount}"

    class Meta:
        verbose_name = "دفع"
        verbose_name_plural = "المدفوعات"

# 9. Complaints
class Complaint(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'قيد الانتظار'),
        ('In Progress', 'قيد التنفيذ'),
        ('Resolved', 'تم الحل'),
    ]
    student = models.ForeignKey(Student, verbose_name='الطالب', on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, verbose_name='الموظف', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(verbose_name='الوصف')
    status = models.CharField(verbose_name='الحالة', max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(verbose_name='تاريخ الإنشاء', auto_now_add=True)

    def __str__(self):
        return f"شكوى #{self.id} - {self.status}"

    class Meta:
        verbose_name = "شكوى"
        verbose_name_plural = "الشكاوى"

# 10. Maintenance
class Maintenance(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'قيد الانتظار'),
        ('In Progress', 'قيد التنفيذ'),
        ('Completed', 'تم الانتهاء'),
    ]
    room = models.ForeignKey(Room, verbose_name='الغرفة', on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, verbose_name='الموظف', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(verbose_name='الوصف')
    status = models.CharField(verbose_name='الحالة', max_length=20, choices=STATUS_CHOICES, default='Pending')
    scheduled_date = models.DateField(verbose_name='تاريخ الصيانة', blank=True, null=True)

    def __str__(self):
        return f"صيانة {self.room} - {self.status}"

    class Meta:
        verbose_name = "صيانة"
        verbose_name_plural = "الصيانات"

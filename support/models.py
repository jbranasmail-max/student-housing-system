from django.db import models
from students.models import Student
from staff.models import Staff
from housing.models import Room


class Complaint(models.Model):
    """الشكاوى"""
    STATUS_CHOICES = [
        ('Pending', 'قيد الانتظار'),
        ('In Progress', 'قيد التنفيذ'),
        ('Resolved', 'تم الحل'),
    ]
    
    student = models.ForeignKey(
        Student, 
        verbose_name='الطالب', 
        on_delete=models.CASCADE,
        related_name='complaints'
    )
    staff = models.ForeignKey(
        Staff, 
        verbose_name='الموظف', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_complaints'
    )
    description = models.TextField(verbose_name='الوصف')
    status = models.CharField(
        verbose_name='الحالة', 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Pending'
    )
    created_at = models.DateTimeField(verbose_name='تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='تاريخ التحديث', auto_now=True)

    def __str__(self):
        return f"شكوى #{self.id} - {self.status}"

    class Meta:
        verbose_name = "شكوى"
        verbose_name_plural = "الشكاوى"
        db_table = 'support_complaint'
        ordering = ['-created_at']


class Maintenance(models.Model):
    """طلبات الصيانة"""
    STATUS_CHOICES = [
        ('Pending', 'قيد الانتظار'),
        ('In Progress', 'قيد التنفيذ'),
        ('Completed', 'تم الانتهاء'),
    ]
    
    room = models.ForeignKey(
        Room, 
        verbose_name='الغرفة', 
        on_delete=models.CASCADE,
        related_name='maintenance_requests'
    )
    staff = models.ForeignKey(
        Staff, 
        verbose_name='الموظف', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_maintenance'
    )
    description = models.TextField(verbose_name='الوصف')
    status = models.CharField(
        verbose_name='الحالة', 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Pending'
    )
    priority = models.CharField(
        verbose_name='الأولوية',
        max_length=10,
        choices=[('Low', 'منخفضة'), ('Medium', 'متوسطة'), ('High', 'عالية')],
        default='Medium'
    )
    scheduled_date = models.DateField(verbose_name='تاريخ الصيانة', blank=True, null=True)
    completed_date = models.DateField(verbose_name='تاريخ الإنجاز', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='تاريخ التحديث', auto_now=True)

    def __str__(self):
        return f"صيانة {self.room} - {self.status}"

    class Meta:
        verbose_name = "صيانة"
        verbose_name_plural = "الصيانات"
        db_table = 'support_maintenance'
        ordering = ['-created_at']

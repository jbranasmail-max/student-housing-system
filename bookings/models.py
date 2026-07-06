from django.db import models
from students.models import Student
from housing.models import Room


class Assignment(models.Model):
    """حجوزات الغرف"""
    STATUS_CHOICES = [
        ('Active', 'نشطة'),
        ('Completed', 'مكتملة'),
        ('Cancelled', 'ملغاة'),
    ]
    
    student = models.ForeignKey(
        Student, 
        verbose_name='الطالب', 
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    room = models.ForeignKey(
        Room, 
        verbose_name='الغرفة', 
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    start_date = models.DateField(verbose_name='تاريخ البداية')
    end_date = models.DateField(verbose_name='تاريخ النهاية', blank=True, null=True)
    status = models.CharField(
        verbose_name='الحالة', 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Active'
    )
    created_at = models.DateTimeField(verbose_name='تاريخ الحجز', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='تاريخ التحديث', auto_now=True)

    class Meta:
        unique_together = ('student', 'room', 'start_date')
        verbose_name = "حجز"
        verbose_name_plural = "الحجوزات"
        db_table = 'bookings_assignment'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} → {self.room}"

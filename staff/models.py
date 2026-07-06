from django.db import models
from core.models import Role


class Staff(models.Model):
    """الموظفين"""
    name = models.CharField(verbose_name='الاسم', max_length=100)
    role = models.ForeignKey(
        Role, 
        verbose_name='الوظيفة', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='staff_members'
    )
    phone = models.CharField(verbose_name='رقم الهاتف', max_length=15, unique=True, blank=True, null=True)
    email = models.EmailField(verbose_name='البريد الإلكتروني', unique=True, blank=True, null=True)
    hire_date = models.DateField(verbose_name='تاريخ التعيين', blank=True, null=True)
    is_active = models.BooleanField(verbose_name='نشط', default=True)
    created_at = models.DateTimeField(verbose_name='تاريخ التسجيل', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "موظف"
        verbose_name_plural = "الموظفين"
        db_table = 'staff_staff'
        ordering = ['name']

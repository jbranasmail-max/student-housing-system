from django.db import models


class Student(models.Model):
    """معلومات الطلاب"""
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
    created_at = models.DateTimeField(verbose_name='تاريخ التسجيل', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='تاريخ التحديث', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "طالب"
        verbose_name_plural = "الطلاب"
        db_table = 'students_student'
        ordering = ['-created_at']

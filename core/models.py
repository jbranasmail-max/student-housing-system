from django.db import models

# ==================================
# النماذج الأساسية المشتركة
# ==================================

class Role(models.Model):
    """الأدوار الوظيفية"""
    role_name = models.CharField(verbose_name='العمل الوظيفي', max_length=50, unique=True)

    def __str__(self):
        return self.role_name
    
    class Meta:
        verbose_name = "العمل الوظيفي"
        verbose_name_plural = "الأعمال الوظيفية"
        db_table = 'core_role'


class PaymentMethod(models.Model):
    """طرق الدفع المتاحة"""
    method_name = models.CharField(verbose_name='طريقة الدفع', max_length=50, unique=True)

    def __str__(self):
        return self.method_name

    class Meta:
        verbose_name = "طريقة الدفع"
        verbose_name_plural = "طرق الدفع"
        db_table = 'core_payment_method'

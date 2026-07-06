from django.db import models
from students.models import Student
from core.models import PaymentMethod


class Payment(models.Model):
    """المدفوعات"""
    student = models.ForeignKey(
        Student, 
        verbose_name='الطالب', 
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(verbose_name='المبلغ', max_digits=10, decimal_places=2)
    payment_date = models.DateField(verbose_name='تاريخ الدفع')
    method = models.ForeignKey(
        PaymentMethod, 
        verbose_name='طريقة الدفع', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='payments'
    )
    notes = models.TextField(verbose_name='ملاحظات', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='تاريخ التسجيل', auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.amount}"

    class Meta:
        verbose_name = "دفع"
        verbose_name_plural = "المدفوعات"
        db_table = 'payments_payment'
        ordering = ['-payment_date']

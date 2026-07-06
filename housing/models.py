from django.db import models


class Building(models.Model):
    """المباني"""
    name = models.CharField(verbose_name='اسم المبنى', max_length=100, unique=True)
    location = models.CharField(verbose_name='الموقع', max_length=255, blank=True, null=True)
    total_floors = models.PositiveIntegerField(verbose_name='عدد الطوابق')
    admin = models.CharField(verbose_name='المسؤول', max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='تاريخ الإنشاء', auto_now_add=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "مبنى"
        verbose_name_plural = "المباني"
        db_table = 'housing_building'


class Room(models.Model):
    """الغرف"""
    building = models.ForeignKey(
        Building, 
        verbose_name='المبنى', 
        on_delete=models.CASCADE,
        related_name='rooms'
    )
    room_number = models.CharField(verbose_name='رقم الغرفة', max_length=10)
    apartment_number = models.CharField(verbose_name='رقم الشقة', max_length=10, blank=True, null=True)
    floor_number = models.IntegerField(verbose_name='الطابق')
    capacity = models.PositiveIntegerField(verbose_name='السعة')
    current_capacity = models.PositiveIntegerField(verbose_name='السعة الحالية', default=0)
    price = models.DecimalField(verbose_name='السعر', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(verbose_name='تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        unique_together = ('building', 'room_number')
        verbose_name = "غرفة"
        verbose_name_plural = "الغرف"
        db_table = 'housing_room'

    def __str__(self):
        return f"{self.building.name} - {self.room_number}"
    
    @property
    def is_available(self):
        """التحقق من توفر مساحة في الغرفة"""
        return self.current_capacity < self.capacity
    
    @property
    def available_beds(self):
        """عدد الأسرّة المتاحة"""
        return self.capacity - self.current_capacity

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from core.models import PaymentMethod


DEFAULT_PAYMENT_METHODS = [
    "نقدي",
    "تحويل بنكي",
    "بطاقة ائتمانية",
    "محفظة إلكترونية",
]


@receiver(post_migrate)
def create_default_payment_methods(sender, **kwargs):
    for name in DEFAULT_PAYMENT_METHODS:
        PaymentMethod.objects.get_or_create(method_name=name)

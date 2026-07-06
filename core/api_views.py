from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from accounts.authz import get_user_role
from accounts.models import UserProfile
from core.models import PaymentMethod


def payment_method_api(request, pk=None):
    """API لإدارة طرق الدفع (للمدير فقط)."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "يرجى تسجيل الدخول"}, status=401)

    role = get_user_role(request.user)
    if role != UserProfile.ROLE_MANAGER:
        return JsonResponse({"success": False, "message": "إدارة طرق الدفع متاحة للمدير فقط"}, status=403)

    if request.method == "GET" and pk:
        payment_method = get_object_or_404(PaymentMethod, pk=pk)
        return JsonResponse(
            {
                "success": True,
                "data": {
                    "id": payment_method.id,
                    "method_name": payment_method.method_name,
                },
            }
        )

    if request.method == "POST" and pk and request.path.endswith("/delete/"):
        payment_method = get_object_or_404(PaymentMethod, pk=pk)
        payment_method.delete()
        return JsonResponse({"success": True, "message": "تم حذف طريقة الدفع بنجاح"})

    if request.method == "POST":
        method_name = (request.POST.get("method_name") or "").strip()
        if not method_name:
            return JsonResponse({"success": False, "error": "اسم طريقة الدفع مطلوب"}, status=400)

        duplicate = PaymentMethod.objects.filter(method_name__iexact=method_name)
        if pk:
            duplicate = duplicate.exclude(pk=pk)
        if duplicate.exists():
            return JsonResponse({"success": False, "error": "طريقة الدفع موجودة مسبقًا"}, status=400)

        try:
            if pk:
                payment_method = get_object_or_404(PaymentMethod, pk=pk)
                payment_method.method_name = method_name
                payment_method.save(update_fields=["method_name"])
                message = "تم تحديث طريقة الدفع بنجاح"
            else:
                payment_method = PaymentMethod.objects.create(method_name=method_name)
                message = "تم إضافة طريقة الدفع بنجاح"
        except IntegrityError:
            return JsonResponse({"success": False, "error": "تعذر حفظ طريقة الدفع بسبب تكرار"}, status=400)

        return JsonResponse(
            {
                "success": True,
                "message": message,
                "payment_method": {
                    "id": payment_method.id,
                    "method_name": payment_method.method_name,
                },
            }
        )

    if request.method == "DELETE" or (request.method == "POST" and request.POST.get("_method") == "DELETE"):
        payment_method = get_object_or_404(PaymentMethod, pk=pk)
        payment_method.delete()
        return JsonResponse({"success": True, "message": "تم حذف طريقة الدفع بنجاح"})

    return JsonResponse({"success": False, "message": "طلب غير صالح"}, status=400)

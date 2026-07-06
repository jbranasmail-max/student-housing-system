from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from accounts.authz import get_user_role
from accounts.models import UserProfile
from core.models import Role
from staff.models import Staff


def staff_api(request, pk=None):
    """API لإدارة الموظفين (للمدير فقط)."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "يرجى تسجيل الدخول"}, status=401)

    role = get_user_role(request.user)
    if role != UserProfile.ROLE_MANAGER:
        return JsonResponse({"success": False, "message": "إدارة الموظفين متاحة للمدير فقط"}, status=403)

    if request.method == "GET" and pk:
        staff_member = get_object_or_404(Staff.objects.select_related("role"), pk=pk)
        profile = getattr(staff_member, "user_profile", None)
        linked_user = profile.user if profile else None
        return JsonResponse(
            {
                "success": True,
                "data": {
                    "id": staff_member.id,
                    "name": staff_member.name,
                    "role_id": staff_member.role_id or "",
                    "role_name": staff_member.role.role_name if staff_member.role else "-",
                    "phone": staff_member.phone or "",
                    "email": staff_member.email or "",
                    "hire_date": str(staff_member.hire_date) if staff_member.hire_date else "",
                    "is_active": staff_member.is_active,
                    "username": linked_user.username if linked_user else "",
                    "account_active": linked_user.is_active if linked_user else False,
                },
            }
        )

    if request.method == "POST" and pk and request.path.endswith("/delete/"):
        staff_member = get_object_or_404(Staff, pk=pk)
        profile = getattr(staff_member, "user_profile", None)
        if profile and profile.user and not profile.user.is_superuser:
            profile.user.delete()
        staff_member.delete()
        return JsonResponse({"success": True, "message": "تم حذف الموظف بنجاح"})

    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        role_id = request.POST.get("role")
        phone = (request.POST.get("phone") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        hire_date = request.POST.get("hire_date")
        is_active = str(request.POST.get("is_active") or "true").lower() in {"true", "1", "on", "yes"}
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        create_account = str(request.POST.get("create_account") or "").lower() in {"true", "1", "on", "yes"}

        if not name or not role_id:
            return JsonResponse({"success": False, "error": "اسم الموظف والمسمى الوظيفي حقول مطلوبة"}, status=400)

        staff_role = get_object_or_404(Role, pk=role_id)

        duplicate_phone = Staff.objects.filter(phone=phone) if phone else Staff.objects.none()
        duplicate_email = Staff.objects.filter(email=email) if email else Staff.objects.none()
        if pk:
            duplicate_phone = duplicate_phone.exclude(pk=pk)
            duplicate_email = duplicate_email.exclude(pk=pk)
        if phone and duplicate_phone.exists():
            return JsonResponse({"success": False, "error": "رقم الهاتف مستخدم لموظف آخر"}, status=400)
        if email and duplicate_email.exists():
            return JsonResponse({"success": False, "error": "البريد الإلكتروني مستخدم لموظف آخر"}, status=400)

        if create_account and not username:
            return JsonResponse({"success": False, "error": "اسم المستخدم مطلوب عند إنشاء حساب دخول"}, status=400)
        if create_account and not pk and not password:
            return JsonResponse({"success": False, "error": "كلمة المرور مطلوبة عند إنشاء حساب دخول"}, status=400)

        if username:
            existing_user = User.objects.filter(username=username)
            if pk:
                staff_member = get_object_or_404(Staff, pk=pk)
                profile = getattr(staff_member, "user_profile", None)
                linked_user_id = profile.user_id if profile else None
                if linked_user_id:
                    existing_user = existing_user.exclude(pk=linked_user_id)
            if existing_user.exists():
                return JsonResponse({"success": False, "error": "اسم المستخدم مستخدم مسبقًا"}, status=400)

        try:
            if pk:
                staff_member = get_object_or_404(Staff, pk=pk)
                staff_member.name = name
                staff_member.role = staff_role
                staff_member.phone = phone or None
                staff_member.email = email or None
                staff_member.hire_date = hire_date or None
                staff_member.is_active = is_active
                staff_member.save()

                profile = getattr(staff_member, "user_profile", None)
                if create_account:
                    if profile and profile.user:
                        user = profile.user
                        user.username = username or user.username
                        user.email = email
                        user.first_name = name
                        user.is_active = is_active
                        if password:
                            user.set_password(password)
                        user.save()
                    else:
                        if not password:
                            return JsonResponse(
                                {"success": False, "error": "كلمة المرور مطلوبة لإنشاء الحساب"},
                                status=400,
                            )
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password=password,
                            first_name=name,
                            is_active=is_active,
                        )
                        UserProfile.objects.create(user=user, role=UserProfile.ROLE_STAFF, staff=staff_member)
                elif profile and profile.user:
                    profile.user.first_name = name
                    profile.user.email = email
                    profile.user.is_active = is_active
                    profile.user.save(update_fields=["first_name", "email", "is_active"])

                action_message = "تم تحديث بيانات الموظف بنجاح"
            else:
                staff_member = Staff.objects.create(
                    name=name,
                    role=staff_role,
                    phone=phone or None,
                    email=email or None,
                    hire_date=hire_date or None,
                    is_active=is_active,
                )

                if create_account:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=name,
                        is_active=is_active,
                    )
                    UserProfile.objects.create(user=user, role=UserProfile.ROLE_STAFF, staff=staff_member)

                action_message = "تم إضافة الموظف بنجاح"
        except IntegrityError:
            return JsonResponse({"success": False, "error": "تعذر حفظ البيانات بسبب تعارض أو تكرار"}, status=400)

        profile = getattr(staff_member, "user_profile", None)
        linked_user = profile.user if profile else None

        return JsonResponse(
            {
                "success": True,
                "message": action_message,
                "staff_member": {
                    "id": staff_member.id,
                    "name": staff_member.name,
                    "role_name": staff_member.role.role_name if staff_member.role else "-",
                    "role_id": staff_member.role_id or "",
                    "phone": staff_member.phone or "-",
                    "email": staff_member.email or "-",
                    "hire_date": str(staff_member.hire_date) if staff_member.hire_date else "-",
                    "is_active": staff_member.is_active,
                    "username": linked_user.username if linked_user else "-",
                    "account_status": "نشط" if linked_user and linked_user.is_active else ("غير نشط" if linked_user else "بدون حساب"),
                },
            }
        )

    if request.method == "DELETE" or (request.method == "POST" and request.POST.get("_method") == "DELETE"):
        staff_member = get_object_or_404(Staff, pk=pk)
        profile = getattr(staff_member, "user_profile", None)
        if profile and profile.user and not profile.user.is_superuser:
            profile.user.delete()
        staff_member.delete()
        return JsonResponse({"success": True, "message": "تم حذف الموظف بنجاح"})

    return JsonResponse({"success": False, "message": "طلب غير صالح"}, status=400)

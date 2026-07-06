from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from accounts.models import UserProfile
from accounts.authz import ROLE_GROUP_MAP


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    app_labels = ["students", "housing", "bookings", "payments", "support", "core", "staff", "dashboard"]

    manager_group, _ = Group.objects.get_or_create(name=ROLE_GROUP_MAP[UserProfile.ROLE_MANAGER])
    staff_group, _ = Group.objects.get_or_create(name=ROLE_GROUP_MAP[UserProfile.ROLE_STAFF])
    student_group, _ = Group.objects.get_or_create(name=ROLE_GROUP_MAP[UserProfile.ROLE_STUDENT])

    # مدير: كل الصلاحيات
    manager_group.permissions.set(Permission.objects.all())

    # موظف: عرض الكل + إدارة الشكاوى والصيانة والحجوزات + إضافة/تعديل المدفوعات
    staff_perm_ids = set(
        Permission.objects.filter(
            content_type__app_label__in=app_labels, codename__startswith="view_"
        ).values_list("id", flat=True)
    )
    staff_codenames = [
        "add_complaint",
        "change_complaint",
        "delete_complaint",
        "add_maintenance",
        "change_maintenance",
        "delete_maintenance",
        "add_assignment",
        "change_assignment",
        "add_payment",
        "change_payment",
    ]
    staff_perm_ids.update(
        Permission.objects.filter(
            content_type__app_label__in=app_labels, codename__in=staff_codenames
        ).values_list("id", flat=True)
    )
    staff_perms = Permission.objects.filter(id__in=staff_perm_ids)
    staff_group.permissions.set(staff_perms)

    # طالب: عرض محدود + إنشاء/تعديل طلباته
    student_codenames = [
        "view_assignment",
        "view_payment",
        "view_complaint",
        "view_maintenance",
        "view_room",
        "view_building",
        "add_complaint",
        "change_complaint",
        "add_payment",
        "add_maintenance",
        "change_maintenance",
    ]
    student_perms = Permission.objects.filter(
        content_type__app_label__in=app_labels, codename__in=student_codenames
    )
    student_group.permissions.set(student_perms)

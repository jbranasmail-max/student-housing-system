from django.conf import settings
from django.db import models

from staff.models import Staff
from students.models import Student


class UserProfile(models.Model):
    ROLE_MANAGER = "manager"
    ROLE_STAFF = "staff"
    ROLE_STUDENT = "student"

    ROLE_CHOICES = [
        (ROLE_MANAGER, "مدير"),
        (ROLE_STAFF, "موظف"),
        (ROLE_STUDENT, "طالب"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    student = models.OneToOneField(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profile",
    )
    staff = models.OneToOneField(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profile",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_user_profile"
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


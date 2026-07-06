from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from accounts.models import UserProfile
from staff.models import Staff
from students.models import Student


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="اسم المستخدم")
    password = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    ROLE_CHOICES = [
        (UserProfile.ROLE_STUDENT, "طالب"),
        (UserProfile.ROLE_STAFF, "موظف"),
    ]

    username = forms.CharField(label="اسم المستخدم", max_length=150)
    email = forms.EmailField(label="البريد الإلكتروني")
    password1 = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput)
    password2 = forms.CharField(label="تأكيد كلمة المرور", widget=forms.PasswordInput)
    full_name = forms.CharField(label="الاسم الكامل", max_length=100)
    phone = forms.CharField(label="رقم الهاتف", max_length=15)
    role = forms.ChoiceField(label="نوع الحساب", choices=ROLE_CHOICES)

    # Student fields
    birth_date = forms.DateField(
        label="تاريخ الميلاد",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    gender = forms.ChoiceField(
        label="الجنس",
        choices=[("M", "ذكر"), ("F", "أنثى")],
        required=False,
    )
    address = forms.CharField(label="العنوان", required=False)
    hire_date = forms.DateField(
        label="تاريخ التعيين (للموظف)",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    staff_role_title = forms.CharField(label="المسمى الوظيفي (للموظف)", required=False, max_length=50)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("اسم المستخدم مستخدم مسبقًا")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("البريد الإلكتروني مستخدم مسبقًا")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        role = cleaned_data.get("role")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("كلمتا المرور غير متطابقتين")

        if role == UserProfile.ROLE_MANAGER:
            raise forms.ValidationError("لا يمكن إنشاء حساب مدير من التسجيل العام")

        if role == UserProfile.ROLE_STUDENT:
            if not cleaned_data.get("birth_date"):
                self.add_error("birth_date", "تاريخ الميلاد مطلوب لحساب الطالب")
            if not cleaned_data.get("gender"):
                self.add_error("gender", "الجنس مطلوب لحساب الطالب")
            if Student.objects.filter(email=cleaned_data.get("email")).exists():
                self.add_error("email", "هذا البريد مرتبط بطالب موجود")
            if Student.objects.filter(phone=cleaned_data.get("phone")).exists():
                self.add_error("phone", "رقم الهاتف مرتبط بطالب موجود")

        if role in {UserProfile.ROLE_STAFF, UserProfile.ROLE_MANAGER}:
            if Staff.objects.filter(email=cleaned_data.get("email")).exists():
                self.add_error("email", "هذا البريد مرتبط بموظف موجود")
            if Staff.objects.filter(phone=cleaned_data.get("phone")).exists():
                self.add_error("phone", "رقم الهاتف مرتبط بموظف موجود")

        if role == UserProfile.ROLE_STAFF:
            if not cleaned_data.get("staff_role_title"):
                self.add_error("staff_role_title", "المسمى الوظيفي مطلوب لحساب الموظف")
            if not cleaned_data.get("hire_date"):
                self.add_error("hire_date", "تاريخ التعيين مطلوب لحساب الموظف")

        return cleaned_data

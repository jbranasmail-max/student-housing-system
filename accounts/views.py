from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect, render

from core.models import Role
from staff.models import Staff
from students.models import Student

from .authz import ROLE_GROUP_MAP
from .forms import LoginForm, RegisterForm
from .models import UserProfile


def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if not user.is_active:
            messages.error(request, "حسابك بانتظار تفعيل المدير.")
            return render(request, "auth/login.html", {"form": form})
        login(request, user)
        return redirect("index")
    return render(request, "auth/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        role = form.cleaned_data["role"]
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
            first_name=form.cleaned_data["full_name"],
            is_active=True,
        )

        profile = UserProfile.objects.create(user=user, role=role)

        if role == UserProfile.ROLE_STUDENT:
            student = Student.objects.create(
                name=form.cleaned_data["full_name"],
                birth_date=form.cleaned_data["birth_date"],
                gender=form.cleaned_data["gender"],
                phone=form.cleaned_data["phone"],
                email=form.cleaned_data["email"],
                address=form.cleaned_data.get("address", ""),
            )
            profile.student = student
            profile.save(update_fields=["student"])

        if role == UserProfile.ROLE_STAFF:
            role_name = form.cleaned_data["staff_role_title"]
            staff_role, _ = Role.objects.get_or_create(role_name=role_name)
            staff_member = Staff.objects.create(
                name=form.cleaned_data["full_name"],
                role=staff_role,
                phone=form.cleaned_data["phone"],
                email=form.cleaned_data["email"],
                hire_date=form.cleaned_data["hire_date"],
                is_active=True,
            )
            profile.staff = staff_member
            profile.save(update_fields=["staff"])

        group_name = ROLE_GROUP_MAP[role]
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

        login(request, user)
        messages.success(request, "تم إنشاء الحساب بنجاح")
        return redirect("index")

    return render(request, "auth/register.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("public_home")

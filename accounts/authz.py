from functools import wraps

from django.http import JsonResponse
from django.shortcuts import redirect

from accounts.models import UserProfile


ROLE_GROUP_MAP = {
    UserProfile.ROLE_MANAGER: "Manager",
    UserProfile.ROLE_STAFF: "Staff",
    UserProfile.ROLE_STUDENT: "Student",
}


def get_user_role(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return UserProfile.ROLE_MANAGER
    profile = getattr(user, "profile", None)
    if profile:
        return profile.role
    return None


def has_role(user, *roles):
    return get_user_role(user) in set(roles)


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.path.startswith("/api/"):
                    return JsonResponse({"success": False, "message": "غير مصرح"}, status=401)
                return redirect("accounts:login")

            if not has_role(request.user, *roles):
                if request.path.startswith("/api/"):
                    return JsonResponse({"success": False, "message": "لا تملك صلاحية"}, status=403)
                return redirect("index")

            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator

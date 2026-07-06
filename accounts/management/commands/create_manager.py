from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand, CommandError

from accounts.authz import ROLE_GROUP_MAP
from accounts.models import UserProfile
from core.models import Role
from staff.models import Staff


class Command(BaseCommand):
    help = "Create a manager account securely from CLI (not via public signup)."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--full-name", required=True)
        parser.add_argument("--phone", required=False, default="")

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]

        if User.objects.filter(username=username).exists():
            raise CommandError("Username already exists.")
        if User.objects.filter(email=email).exists():
            raise CommandError("Email already exists.")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=options["password"],
            first_name=options["full_name"],
            is_staff=True,
            is_superuser=False,
            is_active=True,
        )

        role_obj, _ = Role.objects.get_or_create(role_name="مدير")
        staff_member = Staff.objects.create(
            name=options["full_name"],
            role=role_obj,
            phone=options["phone"] or None,
            email=email,
            is_active=True,
        )
        UserProfile.objects.create(user=user, role=UserProfile.ROLE_MANAGER, staff=staff_member)

        manager_group, _ = Group.objects.get_or_create(name=ROLE_GROUP_MAP[UserProfile.ROLE_MANAGER])
        user.groups.add(manager_group)

        self.stdout.write(self.style.SUCCESS("Manager account created successfully."))


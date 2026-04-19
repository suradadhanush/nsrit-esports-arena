from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Create main super admin"

    def handle(self, *args, **kwargs):
        user, created = User.objects.get_or_create(
            roll_number='25NU1A4436'
        )

        user.email = '25nu1a4436@nsrit.edu.in'
        user.is_staff = True
        user.is_superuser = True
        user.set_password('Admin@1234')  # change later
        user.save()

        self.stdout.write(self.style.SUCCESS("Super admin ready"))
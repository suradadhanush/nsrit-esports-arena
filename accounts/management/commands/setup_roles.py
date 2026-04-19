from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = "Setup roles: Admin and Moderator"

    def handle(self, *args, **kwargs):
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        mod_group, _ = Group.objects.get_or_create(name='Moderator')

        # Admin → all permissions
        admin_group.permissions.set(Permission.objects.all())

        # Moderator → limited permissions
        mod_permissions = Permission.objects.filter(
            codename__in=[
                'view_user', 'change_user',
                'view_player', 'change_player',
                'view_tournament', 'add_tournament', 'change_tournament',
            ]
        )
        mod_group.permissions.set(mod_permissions)

        self.stdout.write(self.style.SUCCESS("Roles created successfully"))
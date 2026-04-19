from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            if not User.objects.filter(email="admin@gmail.com").exists():
                User.objects.create_superuser(
                    email="admin@gmail.com",
                    password="admin123"
                )
        except Exception:
            pass
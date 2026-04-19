from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Registration


@receiver(post_save, sender=Registration)
def auto_confirm_registration(sender, instance, created, **kwargs):
    """
    Auto confirm when payment succeeds
    """
    if instance.payment_status == "SUCCESS" and instance.status != "CONFIRMED":
        instance.confirm()
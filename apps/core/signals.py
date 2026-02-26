from django.conf import settings
from django.core.management import call_command
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def auto_seed_initial_data(sender, **kwargs):
    if not getattr(settings, "AUTO_SEED_ON_STARTUP", True):
        return
    if sender.name != "apps.core":
        return
    call_command("seed_initial_data")

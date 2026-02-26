from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order, OrderStatusEvent
from .services import push_order_status


@receiver(post_save, sender=Order)
def create_status_event_and_push(sender, instance: Order, created: bool, **kwargs):
    if created:
        OrderStatusEvent.objects.create(order=instance, status=instance.status, message="Order created")
    push_order_status(instance)

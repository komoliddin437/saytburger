from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class PushSubscription(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="push_subscriptions")
    endpoint = models.URLField(unique=True)
    p256dh = models.TextField()
    auth = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)


class NotificationLog(TimeStampedModel):
    CHANNELS = (
        ("telegram", "Telegram"),
        ("email", "Email"),
        ("sms", "SMS"),
        ("push", "Push"),
    )
    order = models.ForeignKey("orders.Order", null=True, blank=True, on_delete=models.SET_NULL)
    channel = models.CharField(max_length=16, choices=CHANNELS)
    recipient = models.CharField(max_length=255)
    payload = models.JSONField(default=dict, blank=True)
    is_sent = models.BooleanField(default=False)

from django.db import models

from apps.core.models import TimeStampedModel


class PaymentProvider(models.TextChoices):
    CLICK = "click", "Click"
    PAYME = "payme", "Payme"
    STRIPE = "stripe", "Stripe"


class PaymentTransaction(TimeStampedModel):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="payments")
    provider = models.CharField(max_length=16, choices=PaymentProvider.choices, db_index=True)
    external_id = models.CharField(max_length=128, blank=True, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="UZS")
    is_success = models.BooleanField(default=False, db_index=True)
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.provider} payment #{self.pk}"

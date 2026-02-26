from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class OrderStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    PREPARING = "preparing", "Preparing"
    ON_THE_WAY = "on_the_way", "On the way"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"


class PaymentStatus(models.TextChoices):
    UNPAID = "unpaid", "Unpaid"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"


class Order(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    branch = models.ForeignKey("branches.Branch", on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=32, choices=OrderStatus.choices, default=OrderStatus.PENDING, db_index=True)
    payment_status = models.CharField(
        max_length=32, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID, db_index=True
    )
    delivery_address = models.CharField(max_length=255)
    delivery_lat = models.FloatField(null=True, blank=True)
    delivery_lon = models.FloatField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    promo_code = models.CharField(max_length=64, blank=True)
    bonus_points_used = models.PositiveIntegerField(default=0)
    referral_code = models.CharField(max_length=64, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk}"

    def recalculate_total(self):
        total = self.items.aggregate(total=models.Sum("line_total")).get("total") or Decimal("0.00")
        self.total_amount = total
        self.save(update_fields=["total_amount", "updated_at"])


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT, related_name="order_items")
    product_name = models.CharField(max_length=120)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        indexes = [models.Index(fields=["order"])]

    def save(self, *args, **kwargs):
        self.line_total = self.unit_price * self.quantity
        if not self.product_name:
            self.product_name = self.product.name
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.order_id}: {self.product_name} x{self.quantity}"


class OrderStatusEvent(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_events")
    status = models.CharField(max_length=32, choices=OrderStatus.choices)
    message = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

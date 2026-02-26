from django.db import models
from django.utils.text import slugify

from apps.core.models import TimeStampedModel
from apps.core.utils.geo import haversine_km


class Branch(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=32)
    latitude = models.FloatField()
    longitude = models.FloatField()
    delivery_radius_km = models.FloatField(default=5.0)
    opens_at = models.TimeField()
    closes_at = models.TimeField()
    timezone = models.CharField(max_length=64, default="Asia/Tashkent")
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def distance_km(self, lat: float, lon: float) -> float:
        return haversine_km(lat, lon, self.latitude, self.longitude)

    def can_deliver(self, lat: float, lon: float) -> bool:
        return self.distance_km(lat, lon) <= self.delivery_radius_km


class BranchSettings(TimeStampedModel):
    branch = models.OneToOneField(Branch, on_delete=models.CASCADE, related_name="settings")
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_accepting_orders = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.branch.name} settings"


class ReservationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"


class TableReservation(TimeStampedModel):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="reservations")
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=32)
    guests_count = models.PositiveSmallIntegerField(default=2)
    reserved_for = models.DateTimeField()
    notes = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, choices=ReservationStatus.choices, default=ReservationStatus.PENDING)

    class Meta:
        ordering = ["-reserved_for"]

    def __str__(self) -> str:
        return f"{self.full_name} - {self.branch.name}"

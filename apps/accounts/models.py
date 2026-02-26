from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampedModel


class User(AbstractUser):
    phone = models.CharField(max_length=32, blank=True)
    bonus_points = models.PositiveIntegerField(default=0)
    vip_status = models.CharField(max_length=32, default="standard")
    referral_code = models.CharField(max_length=32, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="referrals")
    preferred_language = models.CharField(max_length=8, default="uz")
    two_factor_enabled = models.BooleanField(default=False)
    preferred_branch = models.ForeignKey(
        "branches.Branch", null=True, blank=True, on_delete=models.SET_NULL, related_name="preferred_users"
    )

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = f"BB{self.username[:8].upper()}"
        super().save(*args, **kwargs)


class BranchRole(models.TextChoices):
    CUSTOMER = "customer", "Customer"
    CHEF = "chef", "Chef"
    COURIER = "courier", "Courier"
    MANAGER = "manager", "Manager"
    ADMIN = "admin", "Admin"


class BranchMembership(TimeStampedModel):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="branch_memberships")
    branch = models.ForeignKey("branches.Branch", on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=32, choices=BranchRole.choices, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "branch", "role")


class WishlistItem(TimeStampedModel):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="wishlist_items")

    class Meta:
        unique_together = ("user", "product")

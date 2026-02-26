from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BranchMembership, User, WishlistItem


@admin.register(User)
class UserAdminExt(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Business",
            {
                "fields": (
                    "phone",
                    "preferred_branch",
                    "bonus_points",
                    "vip_status",
                    "referral_code",
                    "referred_by",
                    "preferred_language",
                    "two_factor_enabled",
                )
            },
        ),
    )


@admin.register(BranchMembership)
class BranchMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "branch", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "branch")


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "product__name")

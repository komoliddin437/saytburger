from django.contrib import admin

from .models import Branch, BranchSettings, TableReservation


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "delivery_radius_km", "is_active")
    search_fields = ("name", "address", "phone")
    list_filter = ("is_active",)


@admin.register(BranchSettings)
class BranchSettingsAdmin(admin.ModelAdmin):
    list_display = ("branch", "min_order_amount", "service_fee", "tax_percent", "is_accepting_orders")


@admin.register(TableReservation)
class TableReservationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "branch", "guests_count", "reserved_for", "status")
    list_filter = ("status", "branch")
    search_fields = ("full_name", "phone", "notes")

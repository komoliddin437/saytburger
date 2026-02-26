from django.contrib import admin

from .models import Order, OrderItem, OrderStatusEvent


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "branch", "status", "payment_status", "total_amount", "created_at")
    list_filter = ("status", "payment_status", "branch")
    search_fields = ("id", "user__username", "delivery_address")
    inlines = [OrderItemInline]


@admin.register(OrderStatusEvent)
class OrderStatusEventAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "created_at")

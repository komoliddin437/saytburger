from django.contrib import admin

from .models import PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "provider", "amount", "currency", "is_success", "created_at")
    list_filter = ("provider", "is_success")
    search_fields = ("order__id", "external_id")

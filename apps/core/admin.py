from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "method", "path", "action", "ip_address")
    list_filter = ("method", "action", "created_at")
    search_fields = ("path", "actor__username", "object_type", "object_id")
    readonly_fields = (
        "created_at",
        "updated_at",
        "actor",
        "action",
        "path",
        "method",
        "object_type",
        "object_id",
        "ip_address",
        "user_agent",
        "metadata",
    )

from django.contrib import admin

from .models import NotificationLog, PushSubscription


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "endpoint", "is_active", "created_at")
    search_fields = ("user__username", "endpoint")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("channel", "recipient", "is_sent", "created_at")
    list_filter = ("channel", "is_sent")

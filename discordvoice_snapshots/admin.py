from django.contrib import admin
from .models import Channel, Snapshot, SnapshotUser, AuditLog


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "channel_type")
    search_fields = ("name", "channel_type")


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    list_display = ("channel", "timestamp")
    list_filter = ("channel", "timestamp")
    search_fields = ("channel__name",)
    date_hierarchy = "timestamp"


@admin.register(SnapshotUser)
class SnapshotUserAdmin(admin.ModelAdmin):
    list_display = ("snapshot", "user")
    list_filter = ("snapshot__channel",)
    search_fields = ("user__username", "snapshot__channel__name")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "timestamp")
    list_filter = ("action", "timestamp")
    search_fields = ("user__username", "action", "old_value", "new_value")
    date_hierarchy = "timestamp"

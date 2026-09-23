from django.contrib import admin
from .models import (
    Channel,
    Snapshot,
    SnapshotUser,
    AuditLog,
    SnapshotTag,
    SnapshotAutomationSettings,
    RetentionPolicy,
)


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "channel_type")
    search_fields = ("name", "channel_type")


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    list_display = ("channel", "timestamp", "tag", "created_by")
    list_filter = ("channel", "timestamp", "tag")
    search_fields = ("channel__name", "created_by__username")
    date_hierarchy = "timestamp"


@admin.register(SnapshotUser)
class SnapshotUserAdmin(admin.ModelAdmin):
    list_display = ("snapshot", "user", "discord_user_id", "discord_username")
    list_filter = ("snapshot__channel",)
    search_fields = ("user__username", "snapshot__channel__name")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "timestamp")
    list_filter = ("action", "timestamp")
    search_fields = ("user__username", "action", "old_value", "new_value")
    date_hierarchy = "timestamp"


@admin.register(SnapshotTag)
class SnapshotTagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(SnapshotAutomationSettings)
class SnapshotAutomationSettingsAdmin(admin.ModelAdmin):
    list_display = ("tag", "enabled", "updated_at")

    def has_add_permission(self, request):
        return not SnapshotAutomationSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RetentionPolicy)
class RetentionPolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "snapshot_days", "audit_days", "enabled")
    list_filter = ("enabled",)
    search_fields = ("name",)

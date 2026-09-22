from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Channel(models.Model):
    name = models.CharField(max_length=255)
    channel_type = models.CharField(max_length=50, blank=True)
    discord_guild_id = models.CharField(max_length=64, blank=True)
    discord_channel_id = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return self.name


class SnapshotTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Snapshot(models.Model):
    class AccessScope(models.TextChoices):
        SELF = "self", "Self"
        CORPORATION = "corporation", "Corporation"
        ALLIANCE = "alliance", "Alliance"
        ADMIN = "admin", "Admin"
        SUPERADMIN = "superadmin", "Superadmin"

    channel = models.ForeignKey(
        Channel,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="snapshots",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    tag = models.ForeignKey(
        SnapshotTag,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="snapshots",
    )
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_snapshots",
    )
    scope = models.CharField(
        max_length=20,
        choices=AccessScope.choices,
        default=AccessScope.SELF,
    )
    visibility = models.CharField(
        max_length=20,
        choices=AccessScope.choices,
        default=AccessScope.SELF,
    )

    def __str__(self):
        return f"{self.channel.name} @ {self.timestamp}"


class SnapshotUser(models.Model):
    snapshot = models.ForeignKey(
        Snapshot,
        on_delete=models.CASCADE,
        related_name="snapshot_users",
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    discord_user_id = models.CharField(max_length=64, null=True, blank=True)
    discord_username = models.CharField(max_length=200, null=True, blank=True)
    voice_channel_name = models.CharField(max_length=255, blank=True)
    voice_channel_id = models.CharField(max_length=64, blank=True)
    is_visible_to_owner = models.BooleanField(default=True)

    class Meta:
        unique_together = ("snapshot", "user", "discord_user_id")

    def __str__(self):
        if self.user:
            return f"{self.user.username} in {self.snapshot}"
        return f"{self.discord_username or self.discord_user_id} in {self.snapshot}"


class ActiveVoiceState(models.Model):
    id = models.BigAutoField(primary_key=True)
    guild_id = models.CharField(max_length=64)
    discord_user_id = models.CharField(max_length=64)
    discord_username = models.CharField(max_length=200, blank=True)
    channel_id = models.CharField(max_length=64)
    channel_name = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("guild_id", "discord_user_id"),
                name="unique_active_voice_user_per_guild",
            )
        ]


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.timestamp} - {self.action}"


class RetentionPolicy(models.Model):
    name = models.CharField(max_length=100, default="default")
    snapshot_days = models.PositiveIntegerField(
        default=365,
        help_text="Days to keep snapshots. Set to 0 to disable snapshot pruning.",
    )
    audit_days = models.PositiveIntegerField(
        default=90,
        help_text="Days to keep audit logs. Set to 0 to disable audit pruning.",
    )
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Retention Policy"
        verbose_name_plural = "Retention Policies"

    def __str__(self):
        return f"{self.name} (snapshots: {self.snapshot_days}d, audit: {self.audit_days}d)"

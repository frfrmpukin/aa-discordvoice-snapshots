from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Channel(models.Model):
    name = models.CharField(max_length=255)
    channel_type = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


class SnapshotTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Snapshot(models.Model):
    channel_name = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    tag = models.ForeignKey(
        SnapshotTag,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="snapshots"
    )

    def __str__(self):
        return f"{self.channel_name} @ {self.timestamp}"


class SnapshotUser(models.Model):
    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE, related_name="snapshot_users")
    # AA user if linked; nullable so we can record Discord-only entries
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # store discord id for unlinked users or for reference
    discord_user_id = models.CharField(max_length=64, null=True, blank=True)
    discord_username = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        unique_together = ("snapshot", "user", "discord_user_id")


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.timestamp} - {self.action}"

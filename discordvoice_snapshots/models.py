from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Channel(models.Model):
    name = models.CharField(max_length=255)
    channel_type = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Snapshot(models.Model):
    channel_name = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    tag = models.ForeignKey(
        "SnapshotTag",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="snapshots"
    )

    def __str__(self):
        return f"{self.channel_name} @ {self.timestamp}"


class SnapshotUser(models.Model):
    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("snapshot", "user")


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)


class SnapshotTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


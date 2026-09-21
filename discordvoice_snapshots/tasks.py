from celery import shared_task
from django.utils import timezone

from .models import Channel, Snapshot
from .utils_cleanup import cleanup_old_snapshots, cleanup_empty_snapshots, cleanup_old_audit_logs, apply_retention_policy


@shared_task
def periodic_snapshot():
    now = timezone.now()
    for channel in Channel.objects.all():
        Snapshot.objects.create(channel=channel)
    return f"Periodic snapshot created at {now}"


@shared_task
def periodic_cleanup(days=30, audit_days=90):
    deleted_old = cleanup_old_snapshots(days=days, user=None)
    deleted_empty = cleanup_empty_snapshots(user=None)
    deleted_audit = cleanup_old_audit_logs(days=audit_days, user=None)
    return (
        f"Cleanup complete: {deleted_old} old snapshots, "
        f"{deleted_empty} empty snapshots, "
        f"{deleted_audit} audit entries"
    )


@shared_task
def periodic_retention_cleanup():
    result = apply_retention_policy(user=None)
    return (
        f"Retention cleanup complete: {result['snapshots']} snapshots pruned, "
        f"{result['audit_logs']} audit logs pruned"
    )

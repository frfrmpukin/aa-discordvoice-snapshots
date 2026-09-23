from django.utils import timezone
from datetime import timedelta
from .models import Snapshot, AuditLog, RetentionPolicy
from .utils import log_action


def get_retention_policy():
    policy = RetentionPolicy.objects.filter(enabled=True).order_by("-updated_at").first()
    if policy:
        return policy
    return RetentionPolicy.objects.create(
        name="default",
        snapshot_days=365,
        audit_days=90,
        enabled=True,
    )


def cleanup_old_snapshots(days=30, user=None):
    if days <= 0:
        return 0
    cutoff = timezone.now() - timedelta(days=days)
    old_snaps = Snapshot.objects.filter(timestamp__lt=cutoff)
    count = old_snaps.count()
    old_snaps.delete()
    log_action(
        user=user,
        action=f"Cleanup: Deleted {count} snapshots older than {days} days",
        old_value=str(days),
        new_value=str(count),
    )
    return count


def cleanup_empty_snapshots(user=None):
    empty = Snapshot.objects.filter(snapshot_users__isnull=True)
    count = empty.count()
    empty.delete()
    log_action(
        user=user,
        action=f"Cleanup: Deleted {count} empty snapshots",
        old_value=str(count),
        new_value=None,
    )
    return count


def cleanup_old_audit_logs(days=90, user=None):
    if days <= 0:
        return 0
    cutoff = timezone.now() - timedelta(days=days)
    old_logs = AuditLog.objects.filter(timestamp__lt=cutoff)
    count = old_logs.count()
    old_logs.delete()
    log_action(
        user=user,
        action=f"Cleanup: Deleted {count} audit log entries older than {days} days",
        old_value=str(days),
        new_value=str(count),
    )
    return count


def apply_retention_policy(user=None):
    policy = get_retention_policy()
    snapshot_deleted = 0
    audit_deleted = 0

    if policy.snapshot_days > 0:
        snapshot_deleted = cleanup_old_snapshots(policy.snapshot_days, user=user)
    if policy.audit_days > 0:
        audit_deleted = cleanup_old_audit_logs(policy.audit_days, user=user)

    return {"snapshots": snapshot_deleted, "audit_logs": audit_deleted, "policy": policy}

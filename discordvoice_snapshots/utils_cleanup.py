from django.utils import timezone
from datetime import timedelta
from .models import Snapshot, SnapshotUser
from .utils import log_action


def cleanup_old_snapshots(days=30, user=None):
    """
    Deletes snapshots older than X days.
    """
    cutoff = timezone.now() - timedelta(days=days)
    old_snaps = Snapshot.objects.filter(timestamp__lt=cutoff)

    count = old_snaps.count()
    log_action(
        user=user,
        action=f"Cleanup: Deleted {count} snapshots older than {days} days",
        old_value=str(count),
        new_value=None
    )

    old_snaps.delete()
    return count


def cleanup_empty_snapshots(user=None):
    """
    Deletes snapshots with no users.
    """
    empty = Snapshot.objects.filter(snapshotuser__isnull=True)
    count = empty.count()

    log_action(
        user=user,
        action=f"Cleanup: Deleted {count} empty snapshots",
        old_value=str(count),
        new_value=None
    )

    empty.delete()
    return count

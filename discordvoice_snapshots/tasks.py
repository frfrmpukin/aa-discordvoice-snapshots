from celery import shared_task
from django.utils import timezone
from .models import Channel, Snapshot

@shared_task
def periodic_snapshot():
    """
    Optional periodic snapshot task.
    Disabled by default. Enable by adding to CELERYBEAT_SCHEDULE.
    """

    now = timezone.now()

    # Example: snapshot all channels
    for channel in Channel.objects.all():
        Snapshot.objects.create(channel=channel)

    return f"Periodic snapshot created at {now}"

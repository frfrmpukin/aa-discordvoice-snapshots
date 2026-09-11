from django.utils import timezone
from .models import AuditLog

def log_action(user, action, old_value=None, new_value=None):
    """
    Creates an audit log entry.
    user: AA User or None
    action: string describing the action
    old_value/new_value: optional text fields
    """
    AuditLog.objects.create(
        user=user,
        action=action,
        timestamp=timezone.now(),
        old_value=old_value,
        new_value=new_value,
    )

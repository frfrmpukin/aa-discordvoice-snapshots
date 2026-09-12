from django.utils import timezone
from .models import AuditLog


def log_action(user, action, old_value=None, new_value=None):
    AuditLog.objects.create(
        user=user,
        action=action,
        timestamp=timezone.now(),
        old_value=old_value,
        new_value=new_value,
    )

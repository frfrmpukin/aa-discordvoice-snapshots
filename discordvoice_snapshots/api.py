from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Snapshot, SnapshotUser, AuditLog

@require_GET
def api_snapshots(request):
    data = [
        {
            "id": s.id,
            "channel": s.channel.name,
            "timestamp": s.timestamp,
        }
        for s in Snapshot.objects.select_related("channel")
    ]
    return JsonResponse({"snapshots": data})

@require_GET
def api_user_snapshots(request, user_id):
    entries = SnapshotUser.objects.filter(user_id=user_id).select_related("snapshot")
    data = [
        {
            "snapshot_id": e.snapshot.id,
            "channel": e.snapshot.channel.name,
            "timestamp": e.snapshot.timestamp,
        }
        for e in entries
    ]
    return JsonResponse({"history": data})

@require_GET
def api_audit_log(request):
    logs = AuditLog.objects.select_related("user").order_by("-timestamp")
    data = [
        {
            "user": log.user.username if log.user else None,
            "action": log.action,
            "timestamp": log.timestamp,
            "old_value": log.old_value,
            "new_value": log.new_value,
        }
        for log in logs
    ]
    return JsonResponse({"audit": data})

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required

from allianceauth.services.modules.discord.models import DiscordUser
from .models import Snapshot, SnapshotUser, AuditLog
from .utils_cleanup import cleanup_old_audit_logs

User = get_user_model()


@require_GET
@permission_required("discordvoice_snapshots.view_snapshot", raise_exception=True)
def api_snapshots(request):
    page = max(1, int(request.GET.get("page", 1)))
    page_size = min(100, max(1, int(request.GET.get("page_size", 25))))

    snapshots = Snapshot.objects.select_related("channel", "tag").order_by("-timestamp")
    total = snapshots.count()
    data = [
        {
            "id": s.id,
            "channel": s.channel.name,
            "timestamp": s.timestamp,
            "tag": s.tag.name if s.tag else None,
        }
        for s in snapshots[(page - 1) * page_size : page * page_size]
    ]
    return JsonResponse({"snapshots": data, "page": page, "page_size": page_size, "total": total})


@require_GET
@permission_required("discordvoice_snapshots.view_snapshot", raise_exception=True)
def api_user_snapshots(request, user_id):
    entries = SnapshotUser.objects.filter(user_id=user_id).select_related(
        "snapshot", "snapshot__channel"
    )
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
@permission_required("discordvoice_snapshots.view_auditlog", raise_exception=True)
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


@require_GET
@permission_required("discordvoice_snapshots.view_snapshot", raise_exception=True)
def api_user_search(request):
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"results": []})

    users = User.objects.filter(username__icontains=q)[:20]
    data = [{"id": u.id, "username": u.username} for u in users]
    return JsonResponse({"results": data})


@require_GET
@permission_required("discordvoice_snapshots.view_auditlog", raise_exception=True)
def api_audit_log_trim(request):
    days = request.GET.get("days", "90")
    try:
        days = int(days)
    except ValueError:
        return JsonResponse({"error": "Invalid days value"}, status=400)

    trimmed = cleanup_old_audit_logs(days=days, user=request.user)
    return JsonResponse({"trimmed": trimmed, "days": days})


@require_GET
@permission_required("discordvoice_snapshots.change_snapshot", raise_exception=True)
def api_discord_user_search(request):
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"results": []})

    discord_users = (
        DiscordUser.objects.filter(username__icontains=q)
        .select_related("user")[:20]
    )
    data = [
        {
            "id": du.user.id if du.user else None,
            "aa_username": du.user.username if du.user else None,
            "discord_username": du.username,
        }
        for du in discord_users
        if du.user
    ]
    return JsonResponse({"results": data})

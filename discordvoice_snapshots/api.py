from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth import get_user_model

from allianceauth.services.modules.discord.models import DiscordUser
from .models import Snapshot, SnapshotUser, AuditLog
from .permissions import editor_required

User = get_user_model()


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


@require_GET
def api_user_search(request):
    """
    AA-style username autocomplete.
    ?q=<partial>
    """
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"results": []})

    users = User.objects.filter(username__icontains=q)[:20]
    data = [
        {
            "id": u.id,
            "username": u.username,
        }
        for u in users
    ]
    return JsonResponse({"results": data})


@editor_required
@require_GET
def api_discord_user_search(request):
    """
    Discord username search.
    ?q=<partial>
    Only editors/admins may use this.
    """
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"results": []})

    discord_users = DiscordUser.objects.filter(username__icontains=q).select_related("user")[:20]
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

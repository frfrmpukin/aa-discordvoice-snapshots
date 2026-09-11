from django.shortcuts import render, get_object_or_404
from .models import Snapshot, SnapshotUser, AuditLog
from .permissions import admin_required, editor_required, viewer_required
from .utils import log_action

@viewer_required
def snapshot_list(request):
    snapshots = Snapshot.objects.select_related("channel").all()
    return render(request, "discordvoice_snapshots/snapshot_list.html", {"snapshots": snapshots})

@viewer_required
def snapshot_detail(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    users = SnapshotUser.objects.filter(snapshot=snapshot)

    log_action(
        user=request.user,
        action=f"Viewed snapshot {snapshot_id}"
    )

    return render(request, "discordvoice_snapshots/snapshot_detail.html", {
        "snapshot": snapshot,
        "users": users
    })

def user_dashboard(request, user_id):
    snapshots = SnapshotUser.objects.filter(user_id=user_id).select_related("snapshot")
    return render(request, "discordvoice_snapshots/user_dashboard.html", {"snapshots": snapshots})

@admin_required
def admin_console(request):
    log_action(
        user=request.user,
        action="Opened snapshot admin console"
    )
    return render(request, "discordvoice_snapshots/admin_console.html")

@admin_required
def audit_log_view(request):
    logs = AuditLog.objects.select_related("user").order_by("-timestamp")
    return render(request, "discordvoice_snapshots/audit_log.html", {"logs": logs})

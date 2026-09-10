from django.shortcuts import render, get_object_or_404
from .models import Snapshot, SnapshotUser
from .permissions import admin_required, editor_required, viewer_required

@viewer_required
def snapshot_list(request):
    snapshots = Snapshot.objects.select_related("channel").all()
    return render(request, "snapshots/snapshot_list.html", {"snapshots": snapshots})

@viewer_required
def snapshot_detail(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    users = SnapshotUser.objects.filter(snapshot=snapshot)
    return render(request, "snapshots/snapshot_detail.html", {"snapshot": snapshot, "users": users})

def user_dashboard(request, user_id):
    snapshots = SnapshotUser.objects.filter(user_id=user_id).select_related("snapshot")
    return render(request, "snapshots/user_dashboard.html", {"snapshots": snapshots})

@admin_required
def admin_console(request):
    return render(request, "snapshots/admin_console.html")

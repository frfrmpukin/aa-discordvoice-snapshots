from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages

from .models import Snapshot, SnapshotUser, Channel
from .permissions import admin_required, editor_required, viewer_required
from .utils import log_action

User = get_user_model()


@editor_required
def snapshot_edit(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    users = SnapshotUser.objects.filter(snapshot=snapshot).select_related("user")

    if request.method == "POST":
        action = request.POST.get("action")

        # Add user
        if action == "add_user":
            username = request.POST.get("username")
            try:
                user = User.objects.get(username=username)
                SnapshotUser.objects.get_or_create(snapshot=snapshot, user=user)

                log_action(
                    user=request.user,
                    action=f"Added user {username} to snapshot {snapshot_id}",
                    old_value=None,
                    new_value=username
                )
                messages.success(request, f"User {username} added.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")

        # Remove user
        elif action == "remove_user":
            user_id = request.POST.get("user_id")
            SnapshotUser.objects.filter(snapshot=snapshot, user_id=user_id).delete()

            log_action(
                user=request.user,
                action=f"Removed user {user_id} from snapshot {snapshot_id}",
                old_value=user_id,
                new_value=None
            )
            messages.success(request, "User removed.")

        # Delete snapshot
        elif action == "delete_snapshot":
            log_action(
                user=request.user,
                action=f"Deleted snapshot {snapshot_id}",
                old_value=str(snapshot),
                new_value=None
            )
            snapshot.delete()
            messages.success(request, "Snapshot deleted.")
            return redirect("discordvoice_snapshots:list")

    return render(
        request,
        "discordvoice_snapshots/snapshot_edit.html",
        {
            "snapshot": snapshot,
            "users": users,
        }
    )

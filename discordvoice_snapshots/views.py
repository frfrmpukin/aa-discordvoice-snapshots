from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages

from .models import Snapshot, SnapshotUser, AuditLog
from .permissions import admin_required, editor_required, viewer_required
from .utils import log_action
from .utils_cleanup import cleanup_old_snapshots, cleanup_empty_snapshots

User = get_user_model()


@viewer_required
def snapshot_list(request):
    snapshots = Snapshot.objects.select_related("channel").all()
    return render(
        request,
        "discordvoice_snapshots/snapshot_list.html",
        {"snapshots": snapshots}
    )


@viewer_required
def snapshot_detail(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    users = SnapshotUser.objects.filter(snapshot=snapshot)

    log_action(
        user=request.user,
        action=f"Viewed snapshot {snapshot_id}"
    )

    return render(
        request,
        "discordvoice_snapshots/snapshot_detail.html",
        {
            "snapshot": snapshot,
            "users": users
        }
    )


@editor_required
def snapshot_edit(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    users = SnapshotUser.objects.filter(snapshot=snapshot).select_related("user")

    if request.method == "POST":
        action = request.POST.get("action")

        # Add AA user (autocomplete)
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

        # Add via Discord username
        elif action == "add_discord_user":
            from allianceauth.services.modules.discord.models import DiscordUser

            discord_name = request.POST.get("discord_username")
            du = DiscordUser.objects.filter(username=discord_name).select_related("user").first()
            if du and du.user:
                SnapshotUser.objects.get_or_create(snapshot=snapshot, user=du.user)

                log_action(
                    user=request.user,
                    action=f"Added Discord user {discord_name} (AA: {du.user.username}) to snapshot {snapshot_id}",
                    old_value=None,
                    new_value=du.user.username
                )
                messages.success(request, f"Discord user {discord_name} added as {du.user.username}.")
            else:
                messages.error(request, "Discord user not found or not linked to an AA user.")

        # Remove single user
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

        # Bulk remove users
        elif action == "bulk_remove":
            ids = request.POST.getlist("bulk_user_ids")
            removed = 0
            for uid in ids:
                removed += SnapshotUser.objects.filter(snapshot=snapshot, user_id=uid).delete()[0]

            log_action(
                user=request.user,
                action=f"Bulk removed {removed} users from snapshot {snapshot_id}",
                old_value=str(ids),
                new_value=None
            )
            messages.success(request, f"Bulk removed {removed} users.")

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


@editor_required
def snapshot_delete(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)

    if request.method == "POST":
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
        "discordvoice_snapshots/snapshot_delete.html",
        {"snapshot": snapshot}
    )


def user_dashboard(request, user_id):
    snapshots = SnapshotUser.objects.filter(user_id=user_id).select_related("snapshot")
    return render(
        request,
        "discordvoice_snapshots/user_dashboard.html",
        {"snapshots": snapshots}
    )


@admin_required
def admin_console(request):
    log_action(
        user=request.user,
        action="Opened snapshot admin console"
    )
    return render(
        request,
        "discordvoice_snapshots/admin_console.html"
    )


@admin_required
def audit_log_view(request):
    logs = AuditLog.objects.select_related("user").order_by("-timestamp")
    return render(
        request,
        "discordvoice_snapshots/audit_log.html",
        {"logs": logs}
    )


@admin_required
def cleanup_tools(request):
    result = None

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "cleanup_old":
            days = int(request.POST.get("days", 30))
            result = cleanup_old_snapshots(days=days, user=request.user)
            messages.success(request, f"Deleted {result} old snapshots.")

        elif action == "cleanup_empty":
            result = cleanup_empty_snapshots(user=request.user)
            messages.success(request, f"Deleted {result} empty snapshots.")

    return render(
        request,
        "discordvoice_snapshots/cleanup_tools.html",
        {"result": result}
    )

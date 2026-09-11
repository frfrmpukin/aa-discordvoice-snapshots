from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.conf import settings
from django.utils import timezone

from allianceauth.services.modules.discord import DiscordApi
from allianceauth.services.modules.discord.models import DiscordUser as AA_DiscordUser

from .models import Snapshot, SnapshotUser, AuditLog, SnapshotTag
from .permissions import admin_required, editor_required, viewer_required
from .utils import log_action
from .utils_cleanup import cleanup_old_snapshots, cleanup_empty_snapshots

User = get_user_model()


@viewer_required
def snapshot_list(request):
    snapshots = Snapshot.objects.select_related("tag").order_by("-timestamp")[:200]
    return render(request, "discordvoice_snapshots/snapshot_list.html", {"snapshots": snapshots})


@viewer_required
def snapshot_detail(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    users = SnapshotUser.objects.filter(snapshot=snapshot).select_related("user")
    log_action(user=request.user, action=f"Viewed snapshot {snapshot_id}")
    return render(request, "discordvoice_snapshots/snapshot_detail.html", {"snapshot": snapshot, "users": users})


@editor_required
def snapshot_edit(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    users = SnapshotUser.objects.filter(snapshot=snapshot).select_related("user")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_user":
            username = request.POST.get("username")
            try:
                user = User.objects.get(username=username)
                SnapshotUser.objects.get_or_create(snapshot=snapshot, user=user)
                log_action(user=request.user, action=f"Added user {username} to snapshot {snapshot_id}", new_value=username)
                messages.success(request, f"User {username} added.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")

        elif action == "add_discord_user":
            discord_name = request.POST.get("discord_username")
            du = AA_DiscordUser.objects.filter(username=discord_name).select_related("user").first()
            if du and du.user:
                SnapshotUser.objects.get_or_create(snapshot=snapshot, user=du.user, defaults={"discord_user_id": du.discord_id, "discord_username": du.username})
                log_action(user=request.user, action=f"Added Discord user {discord_name} (AA: {du.user.username}) to snapshot {snapshot_id}", new_value=du.user.username)
                messages.success(request, f"Discord user {discord_name} added as {du.user.username}.")
            else:
                messages.error(request, "Discord user not found or not linked to an AA user.")

        elif action == "remove_user":
            user_id = request.POST.get("user_id")
            SnapshotUser.objects.filter(snapshot=snapshot, user_id=user_id).delete()
            log_action(user=request.user, action=f"Removed user {user_id} from snapshot {snapshot_id}", old_value=user_id)
            messages.success(request, "User removed.")

        elif action == "bulk_remove":
            ids = request.POST.getlist("bulk_user_ids")
            removed = 0
            for uid in ids:
                removed += SnapshotUser.objects.filter(snapshot=snapshot, user_id=uid).delete()[0]
            log_action(user=request.user, action=f"Bulk removed {removed} users from snapshot {snapshot_id}", old_value=str(ids))
            messages.success(request, f"Bulk removed {removed} users.")

        elif action == "delete_snapshot":
            log_action(user=request.user, action=f"Deleted snapshot {snapshot_id}", old_value=str(snapshot))
            snapshot.delete()
            messages.success(request, "Snapshot deleted.")
            return redirect("discordvoice_snapshots:list")

    return render(request, "discordvoice_snapshots/snapshot_edit.html", {"snapshot": snapshot, "users": users})


@editor_required
def snapshot_delete(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    if request.method == "POST":
        log_action(user=request.user, action=f"Deleted snapshot {snapshot_id}", old_value=str(snapshot))
        snapshot.delete()
        messages.success(request, "Snapshot deleted.")
        return redirect("discordvoice_snapshots:list")
    return render(request, "discordvoice_snapshots/snapshot_delete.html", {"snapshot": snapshot})


def user_dashboard(request, user_id):
    snapshots = SnapshotUser.objects.filter(user_id=user_id).select_related("snapshot").order_by("-snapshot__timestamp")
    return render(request, "discordvoice_snapshots/user_dashboard.html", {"snapshots": snapshots})


@editor_required
def take_snapshot(request):
    if request.method == "POST":
        tag_id = request.POST.get("tag")
        tag = SnapshotTag.objects.filter(id=tag_id).first() if tag_id else None

        api = DiscordApi()
        guild_id = getattr(settings, "DISCORD_GUILD_ID", None)
        if not guild_id:
            messages.error(request, "DISCORD_GUILD_ID is not configured.")
            return redirect("discordvoice_snapshots:list")

        voice_states = api.get_guild_voice_states(guild_id) or []

        snapshot = Snapshot.objects.create(
            channel_name="Multiple Channels",
            tag=tag
        )

        for state in voice_states:
            # adapt to the shape returned by your AA version
            discord_id = None
            discord_username = None
            if isinstance(state, dict):
                discord_id = str(state.get("user_id") or state.get("user", {}).get("id") or state.get("id"))
                discord_username = state.get("username") or state.get("user", {}).get("username")
            else:
                # fallback: try attributes
                discord_id = str(getattr(state, "user_id", None) or getattr(state, "id", None))
                discord_username = getattr(state, "username", None)

            aa_user = None
            if discord_id:
                du = AA_DiscordUser.objects.filter(discord_id=str(discord_id)).select_related("user").first()
                if du:
                    aa_user = du.user

            SnapshotUser.objects.get_or_create(
                snapshot=snapshot,
                user=aa_user,
                discord_user_id=discord_id,
                defaults={"discord_username": discord_username}
            )

        AuditLog.objects.create(
            user=request.user,
            action=f"Take snapshot id={snapshot.id}",
            new_value=f"tag={tag.name if tag else None}"
        )

        messages.success(request, "Snapshot taken.")
        return redirect("discordvoice_snapshots:detail", snapshot.id)

    tags = SnapshotTag.objects.all()
    return render(request, "discordvoice_snapshots/take_snapshot.html", {"tags": tags})


@editor_required
def edit_snapshot(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    if request.method == "POST":
        tag_id = request.POST.get("tag")
        snapshot.tag = SnapshotTag.objects.filter(id=tag_id).first() if tag_id else None
        snapshot.save()
        AuditLog.objects.create(user=request.user, action=f"Edit snapshot id={snapshot.id}", new_value=f"tag={snapshot.tag.name if snapshot.tag else None}")
        messages.success(request, "Snapshot updated.")
        return redirect("discordvoice_snapshots:detail", snapshot.id)

    tags = SnapshotTag.objects.all()
    return render(request, "discordvoice_snapshots/edit_snapshot.html", {"snapshot": snapshot, "tags": tags})


@admin_required
def admin_console(request):
    log_action(user=request.user, action="Opened snapshot admin console")
    return render(request, "discordvoice_snapshots/admin_console.html")


@admin_required
def audit_log_view(request):
    logs = AuditLog.objects.select_related("user").order_by("-timestamp")
    return render(request, "discordvoice_snapshots/audit_log.html", {"logs": logs})


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
    return render(request, "discordvoice_snapshots/cleanup_tools.html", {"result": result})

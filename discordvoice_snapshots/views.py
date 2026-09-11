from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from allianceauth.services.modules.discord import DiscordApi

from .models import Snapshot, SnapshotUser, SnapshotTag, AuditLog, Channel
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
@permission_required("discordvoice_snapshots.view_snapshot", raise_exception=True)
def snapshot_list(request):
    snapshots = Snapshot.objects.select_related("tag").order_by("-timestamp")[:100]
    return render(request, "discordvoice_snapshots/list.html", {"snapshots": snapshots})


@login_required
@permission_required("discordvoice_snapshots.view_snapshot", raise_exception=True)
def snapshot_detail(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    users = SnapshotUser.objects.filter(snapshot=snapshot).select_related("user")
    return render(request, "discordvoice_snapshots/detail.html", {"snapshot": snapshot, "users": users})


@login_required
@permission_required("discordvoice_snapshots.add_snapshot", raise_exception=True)
def take_snapshot(request):
    """
    Manual snapshot: queries Discord via Alliance Auth DiscordApi and stores a snapshot.
    Editors/admins choose an optional tag from the dropdown.
    """
    if request.method == "POST":
        tag_id = request.POST.get("tag")
        tag = SnapshotTag.objects.filter(id=tag_id).first() if tag_id else None

        api = DiscordApi()
        guild_id = getattr(settings, "DISCORD_GUILD_ID", None)
        if not guild_id:
            messages.error(request, "DISCORD_GUILD_ID is not configured.")
            return redirect("discordvoice_snapshots:list")

        # get_guild_voice_states returns a list/dict depending on your AA version; adapt as needed
        voice_states = api.get_guild_voice_states(guild_id)

        snapshot = Snapshot.objects.create(
            channel_name="Multiple Channels",
            timestamp=timezone.now(),
            tag=tag
        )

        # voice_states expected to be iterable of dicts with user_id and username
        for state in voice_states:
            discord_user_id = state.get("user_id") or state.get("user", {}).get("id")
            # try to map to an AA user via allianceauth discord models if available
            aa_user = None
            try:
                from allianceauth.services.modules.discord.models import DiscordUser
                du = DiscordUser.objects.filter(discord_id=str(discord_user_id)).first()
                if du:
                    aa_user = du.user
            except Exception:
                aa_user = None

            SnapshotUser.objects.get_or_create(
                snapshot=snapshot,
                user=aa_user if aa_user else None,
                defaults={}
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


@login_required
@permission_required("discordvoice_snapshots.change_snapshot", raise_exception=True)
def snapshot_edit(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    if request.method == "POST":
        tag_id = request.POST.get("tag")
        snapshot.tag = SnapshotTag.objects.filter(id=tag_id).first() if tag_id else None
        snapshot.save()
        AuditLog.objects.create(
            user=request.user,
            action=f"Edit snapshot id={snapshot.id}",
            old_value="",
            new_value=f"tag={snapshot.tag.name if snapshot.tag else None}"
        )
        messages.success(request, "Snapshot updated.")
        return redirect("discordvoice_snapshots:detail", snapshot.id)

    tags = SnapshotTag.objects.all()
    return render(request, "discordvoice_snapshots/edit_snapshot.html", {"snapshot": snapshot, "tags": tags})


@login_required
@permission_required("discordvoice_snapshots.delete_snapshot", raise_exception=True)
def snapshot_delete(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    if request.method == "POST":
        snapshot.delete()
        AuditLog.objects.create(
            user=request.user,
            action=f"Delete snapshot id={snapshot_id}"
        )
        messages.success(request, "Snapshot deleted.")
        return redirect("discordvoice_snapshots:list")
    return render(request, "discordvoice_snapshots/confirm_delete.html", {"snapshot": snapshot})


# Placeholder views for admin console and user dashboard (implement as needed)
@login_required
@permission_required("discordvoice_snapshots.view_snapshot", raise_exception=True)
def user_dashboard(request, user_id):
    user = get_object_or_404(User, id=user_id)
    snapshots = SnapshotUser.objects.filter(user=user).select_related("snapshot").order_by("-snapshot__timestamp")
    return render(request, "discordvoice_snapshots/user_dashboard.html", {"user": user, "snapshots": snapshots})


@login_required
@permission_required("discordvoice_snapshots.view_auditlog", raise_exception=True)
def audit_log_view(request):
    logs = AuditLog.objects.select_related("user").order_by("-timestamp")[:200]
    return render(request, "discordvoice_snapshots/audit_log.html", {"logs": logs})


@login_required
@permission_required("discordvoice_snapshots.change_snapshot", raise_exception=True)
def cleanup_tools(request):
    # implement cleanup logic or admin UI here
    return render(request, "discordvoice_snapshots/cleanup_tools.html")

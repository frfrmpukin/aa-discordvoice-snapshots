from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from allianceauth.services.modules.discord.models import DiscordUser as AA_DiscordUser

from .models import (
    ActiveVoiceState,
    Snapshot,
    SnapshotUser,
    AuditLog,
    SnapshotTag,
    Channel,
)
from .permissions import (
    admin_required,
    editor_required,
    viewer_required,
    can_view_snapshot,
    can_edit_snapshot,
    can_delete_snapshot,
    can_manage_audit,
)
from .utils import log_action
from .utils_cleanup import (
    cleanup_old_snapshots,
    cleanup_empty_snapshots,
    cleanup_old_audit_logs,
    apply_retention_policy,
    get_retention_policy,
)

User = get_user_model()


@viewer_required
def snapshot_list(request):
    snapshots = Snapshot.objects.select_related("tag", "channel").order_by("-timestamp")

    if not request.user.is_superuser and not request.user.has_perm("discordvoice_snapshots.change_snapshot"):
        snapshots = snapshots.filter(
            Q(snapshot_users__user=request.user) | Q(created_by=request.user)
        ).distinct()

    order_by = request.GET.get("order_by", "-timestamp")
    allowed_order = {
        "timestamp": "timestamp",
        "-timestamp": "-timestamp",
        "channel": "channel__name",
        "-channel": "-channel__name",
        "tag": "tag__name",
        "-tag": "-tag__name",
    }
    if order_by in allowed_order:
        snapshots = snapshots.order_by(allowed_order[order_by])

    page = request.GET.get("page", 1)
    try:
        page = int(page)
    except ValueError:
        page = 1
    page = max(1, page)

    page_size = 25
    start = (page - 1) * page_size
    total = snapshots.count()
    snapshots = snapshots[start:start + page_size]

    return render(
        request,
        "discordvoice_snapshots/snapshot_list.html",
        {
            "snapshots": snapshots,
            "current_order": order_by,
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_previous": page > 1,
            "has_next": start + page_size < total,
        },
    )


@viewer_required
def snapshot_detail(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    if not can_view_snapshot(request.user, snapshot=snapshot):
        raise PermissionDenied

    users = SnapshotUser.objects.filter(snapshot=snapshot).select_related("user")
    if not request.user.is_superuser and not request.user.has_perm("discordvoice_snapshots.change_snapshot"):
        users = users.filter(user=request.user)

    log_action(user=request.user, action=f"Viewed snapshot {snapshot_id}")
    return render(
        request,
        "discordvoice_snapshots/snapshot_detail.html",
        {"snapshot": snapshot, "users": users},
    )


@editor_required
def snapshot_edit(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    if not can_edit_snapshot(request.user, snapshot=snapshot):
        raise PermissionDenied

    users = SnapshotUser.objects.filter(snapshot=snapshot).select_related("user")

    if request.method == "POST":
        action = request.POST.get("action") or "save"

        if action == "save":
            tag_id = request.POST.get("tag")
            snapshot.tag = SnapshotTag.objects.filter(id=tag_id).first() if tag_id else None
            snapshot.save(update_fields=["tag"])
            log_action(
                user=request.user,
                action=f"Updated snapshot {snapshot_id}",
                new_value=f"tag={snapshot.tag.name if snapshot.tag else None}",
            )
            messages.success(request, "Snapshot updated.")
            return redirect("discordvoice_snapshots:detail", snapshot.id)

        if action == "add_user":
            user_id = request.POST.get("user_id")
            username = request.POST.get("username", "").strip()
            user = User.objects.filter(id=user_id).first() if user_id else None
            if user is None and username:
                user = User.objects.filter(username__iexact=username).first()
            if user is None:
                messages.error(request, "Select an Alliance Auth user or enter a valid username.")
            else:
                SnapshotUser.objects.get_or_create(snapshot=snapshot, user=user)
                log_action(
                    user=request.user,
                    action=f"Added user {user.username} to snapshot {snapshot_id}",
                    new_value=user.username,
                )
                messages.success(request, f"User {user.username} added.")

        elif action == "add_discord_user":
            discord_name = request.POST.get("discord_username")
            if not discord_name:
                messages.error(request, "Discord username is required.")
            else:
                du = (
                    AA_DiscordUser.objects.filter(username=discord_name)
                    .select_related("user")
                    .first()
                )
                if du and du.user:
                    SnapshotUser.objects.get_or_create(
                        snapshot=snapshot,
                        user=du.user,
                        defaults={
                            "discord_user_id": str(du.uid),
                            "discord_username": du.username,
                        },
                    )
                    log_action(
                        user=request.user,
                        action=(
                            f"Added Discord user {discord_name} "
                            f"(AA: {du.user.username}) to snapshot {snapshot_id}"
                        ),
                        new_value=du.user.username,
                    )
                    messages.success(
                        request,
                        f"Discord user {discord_name} added as {du.user.username}.",
                    )
                else:
                    messages.error(request, "Discord user not found or not linked.")

        elif action == "remove_user":
            snapshot_user_id = request.POST.get("snapshot_user_id")
            if snapshot_user_id:
                removed = SnapshotUser.objects.filter(
                    snapshot=snapshot, id=snapshot_user_id
                ).delete()[0]
                log_action(
                    user=request.user,
                    action=f"Removed {removed} user record(s) from snapshot {snapshot_id}",
                    old_value=snapshot_user_id,
                )
                messages.success(request, "User removed.")
            else:
                messages.error(request, "Invalid user selection.")

        elif action == "bulk_remove":
            ids = request.POST.getlist("bulk_user_ids")
            removed = 0
            for uid in ids:
                removed += SnapshotUser.objects.filter(
                    snapshot=snapshot, user_id=uid
                ).delete()[0]
            log_action(
                user=request.user,
                action=f"Bulk removed {removed} users from snapshot {snapshot_id}",
                old_value=str(ids),
            )
            messages.success(request, f"Bulk removed {removed} users.")

        elif action == "delete_snapshot":
            if not request.user.has_perm("discordvoice_snapshots.delete_snapshot"):
                raise PermissionDenied
            log_action(
                user=request.user,
                action=f"Deleted snapshot {snapshot_id}",
                old_value=str(snapshot),
            )
            snapshot.delete()
            messages.success(request, "Snapshot deleted.")
            return redirect("discordvoice_snapshots:list")

        return redirect("discordvoice_snapshots:edit", snapshot.id)

    return render(
        request,
        "discordvoice_snapshots/snapshot_edit.html",
        {
            "snapshot": snapshot,
            "users": users,
            "all_users": User.objects.order_by("username"),
            "tags": SnapshotTag.objects.order_by("name"),
        },
    )


@editor_required
def snapshot_delete(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    if not can_delete_snapshot(request.user, snapshot=snapshot):
        raise PermissionDenied

    if request.method == "POST":
        log_action(
            user=request.user,
            action=f"Deleted snapshot {snapshot_id}",
            old_value=str(snapshot),
        )
        snapshot.delete()
        messages.success(request, "Snapshot deleted.")
        return redirect("discordvoice_snapshots:list")
    return render(
        request,
        "discordvoice_snapshots/snapshot_delete.html",
        {"snapshot": snapshot},
    )


@viewer_required
def user_dashboard(request, user_id):
    if request.user.id != user_id and not request.user.is_superuser:
        if not request.user.has_perm("discordvoice_snapshots.change_snapshot"):
            raise PermissionDenied

    snapshots = (
        SnapshotUser.objects.filter(user_id=user_id)
        .select_related("snapshot", "snapshot__channel")
        .order_by("-snapshot__timestamp")
    )

    month = request.GET.get("month")
    current_month = None
    if month:
        try:
            year, month_num = map(int, month.split("-"))
            current_month = year, month_num
            snapshots = snapshots.filter(
                snapshot__timestamp__year=year,
                snapshot__timestamp__month=month_num,
            )
        except ValueError:
            month = None

    if current_month is None:
        today = __import__("datetime").date.today()
        current_month = (today.year, today.month)
        month = f"{today.year}-{today.month:02d}"

    month_date = __import__("datetime").date(current_month[0], current_month[1], 1)
    prev_month = (month_date.replace(day=1) - __import__("datetime").timedelta(days=1)).replace(day=1)
    next_month = (month_date.replace(day=28) + __import__("datetime").timedelta(days=4)).replace(day=1)

    return render(
        request,
        "discordvoice_snapshots/user_dashboard.html",
        {
            "snapshots": snapshots,
            "selected_month": month,
            "month_label": month_date.strftime("%B %Y"),
            "prev_month": prev_month.strftime("%Y-%m"),
            "next_month": next_month.strftime("%Y-%m"),
            "this_month": __import__("datetime").date.today().strftime("%Y-%m"),
        },
    )


@editor_required
def take_snapshot(request):
    if request.method == "POST":
        tag_id = request.POST.get("tag")
        tag = SnapshotTag.objects.filter(id=tag_id).first() if tag_id else None
        guild_id = getattr(settings, "DISCORD_GUILD_ID", None)
        if not guild_id:
            messages.error(request, "DISCORD_GUILD_ID is not configured.")
            return redirect("discordvoice_snapshots:list")

        voice_states = list(
            ActiveVoiceState.objects.filter(guild_id=str(guild_id)).values(
                "discord_user_id",
                "discord_username",
                "channel_id",
                "channel_name",
            )
        )
        if not voice_states:
            messages.error(
                request,
                "There are currently no users in any monitored Discord voice "
                "channel. Join a voice channel before taking a snapshot.",
            )
            return redirect("discordvoice_snapshots:list")

        selected_channel = request.POST.get("channel", "all")
        if selected_channel != "all":
            voice_states = [
                state for state in voice_states
                if state["channel_id"] == selected_channel
            ]
            if not voice_states:
                messages.error(
                    request,
                    "That voice channel is empty. Choose another channel or "
                    "take a server-wide snapshot.",
                )
                return redirect("discordvoice_snapshots:take_snapshot")

            channel = Channel.objects.get_or_create(
                discord_guild_id=str(guild_id),
                discord_channel_id=selected_channel,
                defaults={
                    "name": voice_states[0]["channel_name"],
                    "channel_type": "voice",
                },
            )[0]
        else:
            channel = Channel.objects.get_or_create(
                discord_guild_id=str(guild_id),
                discord_channel_id="",
                defaults={
                    "name": "Server-wide",
                    "channel_type": "voice",
                },
            )[0]

        snapshot = Snapshot.objects.create(
            channel=channel,
            tag=tag,
            created_by=request.user,
            scope=Snapshot.AccessScope.SELF,
            visibility=Snapshot.AccessScope.SELF,
        )

        for state in voice_states:
            discord_id = state["discord_user_id"]
            discord_username = state["discord_username"]
            aa_user = None
            if discord_id:
                du = (
                    AA_DiscordUser.objects.filter(uid=int(discord_id))
                    .select_related("user")
                    .first()
                )
                if du:
                    aa_user = du.user

            SnapshotUser.objects.get_or_create(
                snapshot=snapshot,
                user=aa_user,
                discord_user_id=discord_id,
                defaults={
                    "discord_username": discord_username,
                    "voice_channel_id": state["channel_id"],
                    "voice_channel_name": state["channel_name"],
                },
            )

        AuditLog.objects.create(
            user=request.user,
            action=f"Take snapshot id={snapshot.id}",
            new_value=f"tag={tag.name if tag else None}",
        )
        messages.success(request, "Snapshot taken.")
        return redirect("discordvoice_snapshots:detail", snapshot.id)

    guild_id = getattr(settings, "DISCORD_GUILD_ID", None)
    channels = (
        ActiveVoiceState.objects.filter(guild_id=str(guild_id))
        .values("channel_id", "channel_name")
        .distinct()
        .order_by("channel_name")
        if guild_id
        else []
    )
    return render(
        request,
        "discordvoice_snapshots/take_snapshot.html",
        {"tags": SnapshotTag.objects.all(), "channels": channels},
    )


@editor_required
def edit_snapshot(request, snapshot_id):
    snapshot = get_object_or_404(Snapshot, id=snapshot_id)
    if request.method == "POST":
        tag_id = request.POST.get("tag")
        snapshot.tag = SnapshotTag.objects.filter(id=tag_id).first() if tag_id else None
        snapshot.save()
        AuditLog.objects.create(
            user=request.user,
            action=f"Edit snapshot id={snapshot.id}",
            new_value=f"tag={snapshot.tag.name if snapshot.tag else None}",
        )
        messages.success(request, "Snapshot updated.")
        return redirect("discordvoice_snapshots:detail", snapshot.id)

    tags = SnapshotTag.objects.all()
    return render(
        request,
        "discordvoice_snapshots/edit_snapshot.html",
        {"snapshot": snapshot, "tags": tags},
    )


@admin_required
def admin_console(request):
    log_action(user=request.user, action="Opened snapshot admin console")
    return render(request, "discordvoice_snapshots/admin_console.html")


@admin_required
def audit_log_view(request):
    logs = AuditLog.objects.select_related("user").order_by("-timestamp")
    return render(
        request,
        "discordvoice_snapshots/audit_log.html",
        {"logs": logs},
    )


@admin_required
def cleanup_tools(request):
    result = None
    policy = get_retention_policy()
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "cleanup_old":
            days = int(request.POST.get("days", 30))
            result = cleanup_old_snapshots(days=days, user=request.user)
            messages.success(request, f"Deleted {result} old snapshots.")
        elif action == "cleanup_empty":
            result = cleanup_empty_snapshots(user=request.user)
            messages.success(request, f"Deleted {result} empty snapshots.")
        elif action == "cleanup_audit":
            days = int(request.POST.get("audit_days", 90))
            result = cleanup_old_audit_logs(days=days, user=request.user)
            messages.success(request, f"Deleted {result} old audit log entries.")
        elif action == "save_policy":
            days = int(request.POST.get("snapshot_days", 365))
            audit_days = int(request.POST.get("audit_days", 90))
            policy.snapshot_days = max(0, days)
            policy.audit_days = max(0, audit_days)
            policy.enabled = request.POST.get("enabled") == "on"
            policy.save()
            result = {"snapshots": policy.snapshot_days, "audit_logs": policy.audit_days}
            messages.success(request, "Retention policy updated.")

    return render(
        request,
        "discordvoice_snapshots/cleanup_tools.html",
        {"result": result, "policy": policy},
    )

from functools import wraps

from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)

from .models import Snapshot


def _is_site_admin(user):
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.is_staff)
    )


admin_required = user_passes_test(_is_site_admin)


def _login_and_permission(perm):
    def decorator(view_func):
        @login_required
        @permission_required(perm, raise_exception=True)
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def _scope_rank(scope):
    order = {
        Snapshot.AccessScope.SELF: 0,
        Snapshot.AccessScope.CORPORATION: 1,
        Snapshot.AccessScope.ALLIANCE: 2,
        Snapshot.AccessScope.ADMIN: 3,
        Snapshot.AccessScope.SUPERADMIN: 4,
    }
    if scope is None:
        return 0
    if isinstance(scope, str):
        scope = scope.lower()
    return order.get(scope, -1)


def _user_org_value(user, org_key):
    if not user or not getattr(user, "is_authenticated", False):
        return None

    profile = getattr(user, "profile", None)
    if profile is None:
        return None

    value = getattr(profile, org_key, None)
    if value is None:
        value = getattr(profile, f"{org_key}_id", None)

    if hasattr(value, "id"):
        return value.id
    return value


def _user_access_scope(user):
    if not user or not getattr(user, "is_authenticated", False):
        return Snapshot.AccessScope.SELF
    if user.is_superuser:
        return Snapshot.AccessScope.SUPERADMIN
    if user.has_perm("discordvoice_snapshots.view_auditlog") or user.has_perm(
        "discordvoice_snapshots.delete_snapshot"
    ):
        return Snapshot.AccessScope.ADMIN
    if user.has_perm("discordvoice_snapshots.change_snapshot"):
        return Snapshot.AccessScope.ALLIANCE
    if user.has_perm("discordvoice_snapshots.view_snapshot"):
        return Snapshot.AccessScope.CORPORATION
    if _user_org_value(user, "alliance") is not None:
        return Snapshot.AccessScope.ALLIANCE
    if _user_org_value(user, "corporation") is not None:
        return Snapshot.AccessScope.CORPORATION
    return Snapshot.AccessScope.SELF


def _same_org(user, other_user, org_key):
    if not user or not other_user:
        return False
    return _user_org_value(user, org_key) is not None and _user_org_value(
        user, org_key
    ) == _user_org_value(other_user, org_key)


def can_view_snapshot(user, snapshot=None):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if user.has_perm("discordvoice_snapshots.view_snapshot"):
        return True
    if user.has_perm("discordvoice_snapshots.change_snapshot"):
        return True
    if user.has_perm("discordvoice_snapshots.add_snapshot"):
        return True
    if snapshot is None:
        return False

    if snapshot.created_by_id == user.id:
        return True
    if snapshot.snapshot_users.filter(user_id=user.id).exists():
        return True

    visibility = snapshot.visibility or snapshot.scope or Snapshot.AccessScope.SELF
    user_scope = _user_access_scope(user)
    user_rank = _scope_rank(user_scope)
    required_rank = _scope_rank(visibility)

    if user_rank < required_rank:
        return False

    if visibility == Snapshot.AccessScope.CORPORATION:
        return _same_org(user, snapshot.created_by, "corporation")
    if visibility == Snapshot.AccessScope.ALLIANCE:
        return _same_org(user, snapshot.created_by, "alliance")
    if visibility in (Snapshot.AccessScope.ADMIN, Snapshot.AccessScope.SUPERADMIN):
        return user_rank >= required_rank

    return False


def can_edit_snapshot(user, snapshot=None):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if user.has_perm("discordvoice_snapshots.change_snapshot"):
        if snapshot is None:
            return True
        if snapshot.created_by_id == user.id:
            return True
        user_scope = _user_access_scope(user)
        visibility = snapshot.visibility or snapshot.scope or Snapshot.AccessScope.SELF
        if _scope_rank(user_scope) >= _scope_rank(visibility):
            return True
        return False
    if snapshot is not None:
        return snapshot.created_by_id == user.id and user.has_perm(
            "discordvoice_snapshots.change_snapshot"
        )
    return False


def can_delete_snapshot(user, snapshot=None):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if user.has_perm("discordvoice_snapshots.delete_snapshot"):
        return True
    if snapshot is not None:
        return (
            snapshot.created_by_id == user.id
            and user.has_perm("discordvoice_snapshots.change_snapshot")
        )
    return False


def can_manage_audit(user):
    return user.is_authenticated and (
        user.is_superuser
        or user.has_perm("discordvoice_snapshots.view_auditlog")
        or user.has_perm("discordvoice_snapshots.delete_snapshot")
    )


viewer_required = _login_and_permission("discordvoice_snapshots.view_snapshot")
editor_required = _login_and_permission("discordvoice_snapshots.change_snapshot")

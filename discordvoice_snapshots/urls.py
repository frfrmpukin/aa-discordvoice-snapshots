from django.urls import path
from . import views, api

app_name = "discordvoice_snapshots"

urlpatterns = [
    path("", views.snapshot_list, name="list"),
    path("take/", views.take_snapshot, name="take_snapshot"),
    path("<int:snapshot_id>/", views.snapshot_detail, name="detail"),
    path("<int:snapshot_id>/edit/", views.snapshot_edit, name="edit"),
    path("<int:snapshot_id>/delete/", views.snapshot_delete, name="delete"),

    path("user/<int:user_id>/", views.user_dashboard, name="user_dashboard"),

    path("admin/", views.admin_console, name="admin_console"),
    path("admin/audit/", views.audit_log_view, name="audit_log"),
    path("admin/cleanup/", views.cleanup_tools, name="cleanup_tools"),

    path("api/", api.api_snapshots, name="api_snapshots"),
    path("api/user/<int:user_id>/", api.api_user_snapshots, name="api_user_snapshots"),
    path("api/audit/", api.api_audit_log, name="api_audit_log"),
    path("api/user-search/", api.api_user_search, name="api_user_search"),
    path(
        "api/discord-user-search/",
        api.api_discord_user_search,
        name="api_discord_user_search",
    ),
]

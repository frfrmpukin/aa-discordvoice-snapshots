urlpatterns = [
    path("", views.snapshot_list, name="list"),
    path("<int:snapshot_id>/", views.snapshot_detail, name="detail"),
    path("<int:snapshot_id>/edit/", views.snapshot_edit, name="edit"),
    path("user/<int:user_id>/", views.user_dashboard, name="user_dashboard"),
    path("admin/", views.admin_console, name="admin_console"),
    path("admin/audit/", views.audit_log_view, name="audit_log"),

    # API
    path("api/", api.api_snapshots, name="api_snapshots"),
    path("api/user/<int:user_id>/", api.api_user_snapshots, name="api_user_snapshots"),
    path("api/audit/", api.api_audit_log, name="api_audit_log"),
]

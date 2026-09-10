from django.urls import path
from . import views

app_name = "discordvoice_snapshots"

urlpatterns = [
    path("", views.snapshot_list, name="list"),
    path("<int:snapshot_id>/", views.snapshot_detail, name="detail"),
    path("user/<int:user_id>/", views.user_dashboard, name="user_dashboard"),
    path("admin/", views.admin_console, name="admin_console"),
]

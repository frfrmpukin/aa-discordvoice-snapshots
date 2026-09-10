from allianceauth.permissions import site_admin_required
from django.contrib.auth.decorators import permission_required

admin_required = site_admin_required
editor_required = permission_required("discordvoice_snapshots.change_snapshot")
viewer_required = permission_required("discordvoice_snapshots.view_snapshot")

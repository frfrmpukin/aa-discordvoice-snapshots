from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps


APP_LABEL = "discordvoice_snapshots"


VIEWER_PERMS = [
    "view_snapshot",
    "view_snapshotuser",
]

EDITOR_PERMS = VIEWER_PERMS + [
    "add_snapshotuser",
    "change_snapshotuser",
    "delete_snapshotuser",
    "change_snapshot",
]

ADMIN_PERMS = EDITOR_PERMS + [
    "add_snapshot",
    "change_snapshot",
    "delete_snapshot",
    "view_auditlog",
]


class Command(BaseCommand):
    help = "Creates and assigns permissions for Viewer, Editor, and Admin groups for Discord Voice Snapshots."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force-create",
            action="store_true",
            help="Create groups even if they already exist.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Configuring Discord Voice Snapshot groups…"))

        # Ensure app is installed
        if not apps.is_installed(APP_LABEL):
            self.stdout.write(self.style.ERROR(f"App '{APP_LABEL}' is not installed."))
            return

        # Create or fetch groups
        viewer_group, _ = Group.objects.get_or_create(name="Viewer")
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        admin_group, _ = Group.objects.get_or_create(name="Admin")

        # Assign permissions
        self.assign_perms(viewer_group, VIEWER_PERMS)
        self.assign_perms(editor_group, EDITOR_PERMS)
        self.assign_perms(admin_group, ADMIN_PERMS)

        self.stdout.write(self.style.SUCCESS("Viewer, Editor, and Admin groups configured successfully."))

    def assign_perms(self, group, perm_list):
        for perm_codename in perm_list:
            try:
                perm = Permission.objects.get(codename=perm_codename, content_type__app_label=APP_LABEL)
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Permission '{perm_codename}' not found for app '{APP_LABEL}'.")
                )

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

class Command(BaseCommand):
    help = "Create default groups (Viewer, Editor, Admin) and assign snapshot model permissions. Integrates with Alliance Auth group names if present."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force-create",
            action="store_true",
            help="Create Snapshot-specific groups if Alliance Auth groups are not present."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        from django.apps import apps

        # Models we need permissions for
        Snapshot = apps.get_model("discordvoice_snapshots", "Snapshot")
        SnapshotUser = apps.get_model("discordvoice_snapshots", "SnapshotUser")
        AuditLog = apps.get_model("discordvoice_snapshots", "AuditLog")

        # ContentTypes
        ct_snapshot = ContentType.objects.get_for_model(Snapshot)
        ct_snapshotuser = ContentType.objects.get_for_model(SnapshotUser)
        ct_audit = ContentType.objects.get_for_model(AuditLog)

        # Permission codenames we will use
        perms = {
            "snapshot": {
                "add": Permission.objects.get(codename="add_snapshot", content_type=ct_snapshot),
                "change": Permission.objects.get(codename="change_snapshot", content_type=ct_snapshot),
                "delete": Permission.objects.get(codename="delete_snapshot", content_type=ct_snapshot),
                "view": Permission.objects.get(codename="view_snapshot", content_type=ct_snapshot),
            },
            "snapshotuser": {
                "add": Permission.objects.get(codename="add_snapshotuser", content_type=ct_snapshotuser),
                "change": Permission.objects.get(codename="change_snapshotuser", content_type=ct_snapshotuser),
                "delete": Permission.objects.get(codename="delete_snapshotuser", content_type=ct_snapshotuser),
                "view": Permission.objects.get(codename="view_snapshotuser", content_type=ct_snapshotuser),
            },
            "auditlog": {
                "view": Permission.objects.get(codename="view_auditlog", content_type=ct_audit),
            },
        }

        # Alliance Auth canonical group names we will try to use if they exist
        aa_group_map = {
            "Viewer": "viewer",
            "Editor": "editor",
            "Admin": "admin",
            "SuperAdmin": "superadmin",
        }

        created_groups = []

        # Helper to add perms to a group
        def add_perms(group, permission_list):
            for p in permission_list:
                group.permissions.add(p)

        # Try to find Alliance Auth groups; if found, assign perms accordingly
        found_any_aa_group = False
        for aa_name, role_key in aa_group_map.items():
            try:
                g = Group.objects.get(name=aa_name)
                found_any_aa_group = True
                self.stdout.write(self.style.SUCCESS(f"Found existing group '{aa_name}', assigning snapshot permissions."))

                if role_key == "viewer":
                    add_perms(g, [perms["snapshot"]["view"], perms["snapshotuser"]["view"]])
                    # viewers can also view audit logs if you want; be conservative and not add audit view here
                elif role_key == "editor":
                    add_perms(g, [
                        perms["snapshot"]["view"],
                        perms["snapshotuser"]["add"],
                        perms["snapshotuser"]["change"],
                        perms["snapshotuser"]["delete"],
                    ])
                elif role_key == "admin":
                    add_perms(g, [
                        perms["snapshot"]["add"],
                        perms["snapshot"]["change"],
                        perms["snapshot"]["delete"],
                        perms["snapshot"]["view"],
                        perms["snapshotuser"]["add"],
                        perms["snapshotuser"]["change"],
                        perms["snapshotuser"]["delete"],
                        perms["snapshotuser"]["view"],
                        perms["auditlog"]["view"],
                    ])
                elif role_key == "superadmin":
                    # SuperAdmin: give everything (same as admin plus any future perms)
                    add_perms(g, [
                        perms["snapshot"]["add"],
                        perms["snapshot"]["change"],
                        perms["snapshot"]["delete"],
                        perms["snapshot"]["view"],
                        perms["snapshotuser"]["add"],
                        perms["snapshotuser"]["change"],
                        perms["snapshotuser"]["delete"],
                        perms["snapshotuser"]["view"],
                        perms["auditlog"]["view"],
                    ])
                created_groups.append(g.name)
            except Group.DoesNotExist:
                # skip if not present
                continue

        # If no Alliance Auth groups found and --force-create provided, create Snapshot-specific groups
        if not found_any_aa_group and options["force_create"]:
            self.stdout.write(self.style.WARNING("No Alliance Auth groups found; creating Snapshot-specific groups."))

            # Viewer
            g_viewer, _ = Group.objects.get_or_create(name="Snapshot Viewer")
            add_perms(g_viewer, [perms["snapshot"]["view"], perms["snapshotuser"]["view"]])
            created_groups.append(g_viewer.name)

            # Editor
            g_editor, _ = Group.objects.get_or_create(name="Snapshot Editor")
            add_perms(g_editor, [
                perms["snapshot"]["view"],
                perms["snapshotuser"]["add"],
                perms["snapshotuser"]["change"],
                perms["snapshotuser"]["delete"],
            ])
            created_groups.append(g_editor.name)

            # Admin
            g_admin, _ = Group.objects.get_or_create(name="Snapshot Admin")
            add_perms(g_admin, [
                perms["snapshot"]["add"],
                perms["snapshot"]["change"],
                perms["snapshot"]["delete"],
                perms["snapshot"]["view"],
                perms["snapshotuser"]["add"],
                perms["snapshotuser"]["change"],
                perms["snapshotuser"]["delete"],
                perms["snapshotuser"]["view"],
                perms["auditlog"]["view"],
            ])
            created_groups.append(g_admin.name)

        # Always ensure superusers retain full access (superusers bypass group perms by default)
        self.stdout.write(self.style.SUCCESS(f"Assigned permissions to groups: {', '.join(created_groups) if created_groups else 'none (no changes)'}"))
        self.stdout.write(self.style.SUCCESS("Done."))

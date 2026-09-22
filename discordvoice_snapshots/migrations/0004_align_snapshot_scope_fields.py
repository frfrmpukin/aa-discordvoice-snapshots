from django.db import migrations, models


def normalize_legacy_scope_values(apps, schema_editor):
    Snapshot = apps.get_model("discordvoice_snapshots", "Snapshot")
    Snapshot.objects.filter(scope="user").update(scope="self")
    Snapshot.objects.filter(visibility="user").update(visibility="self")


class Migration(migrations.Migration):

    dependencies = [
        ("discordvoice_snapshots", "0003_snapshot_visibility_and_retention_policy"),
    ]

    operations = [
        migrations.RunPython(
            normalize_legacy_scope_values,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="snapshot",
            name="scope",
            field=models.CharField(
                choices=[
                    ("self", "Self"),
                    ("corporation", "Corporation"),
                    ("alliance", "Alliance"),
                    ("admin", "Admin"),
                    ("superadmin", "Superadmin"),
                ],
                default="self",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="snapshot",
            name="visibility",
            field=models.CharField(
                choices=[
                    ("self", "Self"),
                    ("corporation", "Corporation"),
                    ("alliance", "Alliance"),
                    ("admin", "Admin"),
                    ("superadmin", "Superadmin"),
                ],
                default="self",
                max_length=20,
            ),
        ),
    ]

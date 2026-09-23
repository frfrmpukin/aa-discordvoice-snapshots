from django.db import migrations, models
import django.db.models.deletion


def create_automatic_snapshot_settings(apps, schema_editor):
    SnapshotTag = apps.get_model("discordvoice_snapshots", "SnapshotTag")
    SnapshotAutomationSettings = apps.get_model(
        "discordvoice_snapshots", "SnapshotAutomationSettings"
    )
    tag, _ = SnapshotTag.objects.get_or_create(name="Automatic Snapshot")
    SnapshotAutomationSettings.objects.get_or_create(tag=tag)


class Migration(migrations.Migration):

    dependencies = [
        ("discordvoice_snapshots", "0007_alter_activevoicestate_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="SnapshotAutomationSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("enabled", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tag",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="automatic_snapshot_settings",
                        to="discordvoice_snapshots.snapshottag",
                    ),
                ),
            ],
            options={
                "verbose_name": "Automatic Snapshot Settings",
                "verbose_name_plural": "Automatic Snapshot Settings",
            },
        ),
        migrations.RunPython(
            create_automatic_snapshot_settings,
            migrations.RunPython.noop,
        ),
    ]

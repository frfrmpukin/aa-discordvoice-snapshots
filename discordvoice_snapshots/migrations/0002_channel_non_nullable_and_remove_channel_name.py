from django.db import migrations, models


def forwards(apps, schema_editor):
    # No data migration required here because channel should already be populated.
    # This forwards step is intentionally empty; the schema operations below handle the change.
    pass


def backwards(apps, schema_editor):
    # On reverse, re-create channel_name from channel if present.
    Snapshot = apps.get_model("discordvoice_snapshots", "Snapshot")
    for snap in Snapshot.objects.select_related("channel").all():
        if snap.channel:
            snap.channel_name = snap.channel.name
            snap.save(update_fields=["channel_name"])


class Migration(migrations.Migration):

    dependencies = [
        ("discordvoice_snapshots", "0001_initial"),
    ]

    operations = [
        # 1) Make channel non-nullable (AlterField)
        migrations.AlterField(
            model_name="snapshot",
            name="channel",
            field=models.ForeignKey(
                to="discordvoice_snapshots.Channel",
                on_delete=models.CASCADE,
                related_name="snapshots",
            ),
        ),
        # 2) Remove the old channel_name field
        migrations.RemoveField(
            model_name="snapshot",
            name="channel_name",
        ),
    ]


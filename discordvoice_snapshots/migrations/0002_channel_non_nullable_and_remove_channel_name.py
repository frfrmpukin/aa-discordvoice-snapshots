from django.db import migrations, models


def forwards(apps, schema_editor):
    Channel = apps.get_model("discordvoice_snapshots", "Channel")
    Snapshot = apps.get_model("discordvoice_snapshots", "Snapshot")

    fallback_channel, _ = Channel.objects.get_or_create(
        name="Unknown Channel",
        channel_type="voice",
    )

    for snapshot in Snapshot.objects.filter(channel__isnull=True):
        snapshot.channel = fallback_channel
        snapshot.save(update_fields=["channel"])


def backwards(apps, schema_editor):
    Snapshot = apps.get_model("discordvoice_snapshots", "Snapshot")
    for snapshot in Snapshot.objects.select_related("channel").all():
        if snapshot.channel:
            snapshot.channel_name = snapshot.channel.name
            snapshot.save(update_fields=["channel_name"])


class Migration(migrations.Migration):

    dependencies = [
        ("discordvoice_snapshots", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="snapshot",
            name="channel",
            field=models.ForeignKey(
                to="discordvoice_snapshots.Channel",
                on_delete=models.CASCADE,
                related_name="snapshots",
            ),
        ),
        migrations.RemoveField(
            model_name="snapshot",
            name="channel_name",
        ),
    ]


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discordvoice_snapshots", "0005_active_voice_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="channel",
            name="discord_channel_id",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="channel",
            name="discord_guild_id",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="snapshotuser",
            name="voice_channel_id",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="snapshotuser",
            name="voice_channel_name",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

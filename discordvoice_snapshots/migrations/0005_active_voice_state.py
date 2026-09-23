from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discordvoice_snapshots", "0004_align_snapshot_scope_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="ActiveVoiceState",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("guild_id", models.CharField(max_length=64)),
                ("discord_user_id", models.CharField(max_length=64)),
                ("discord_username", models.CharField(blank=True, max_length=200)),
                ("channel_id", models.CharField(max_length=64)),
                ("channel_name", models.CharField(max_length=255)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("guild_id", "discord_user_id"),
                        name="unique_active_voice_user_per_guild",
                    )
                ],
            },
        ),
    ]

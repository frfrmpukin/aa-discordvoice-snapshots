from django.apps import AppConfig
from . import __version__

class DiscordVoiceSnapshotConfig(AppConfig):
    name = "aa_discord_voicesnapshot"
    verbose_name = f"Discord Voice Snapshot ({__version__})"

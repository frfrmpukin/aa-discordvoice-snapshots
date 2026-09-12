from django.apps import AppConfig
from . import __version__

class DiscordVoiceSnapshotsConfig(AppConfig):
    name = "discordvoice_snapshots"
    verbose_name = f"Discord Voice Snapshots ({__version__})"

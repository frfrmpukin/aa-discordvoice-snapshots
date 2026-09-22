from django.apps import AppConfig
from . import __version__


class DiscordVoiceSnapshotsConfig(AppConfig):
    name = "discordvoice_snapshots"
    verbose_name = f"Discord Voice Snapshots ({__version__})"

    def ready(self):
        import discordvoice_snapshots.auth_hooks  # noqa: F401
        import discordvoice_snapshots.navigation  # noqa: F401

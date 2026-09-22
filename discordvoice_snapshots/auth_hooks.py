from allianceauth import hooks
from allianceauth.services.hooks import UrlHook

from . import urls


@hooks.register("url_hook")
def register_urls():
    return UrlHook(
        urls=urls,
        namespace="discordvoice_snapshots",
        base_url=r"^discordvoice-snapshots/",
    )


@hooks.register("discord_cogs_hook")
def register_cogs():
    return ["discordvoice_snapshots.cogs.voice_snapshots"]

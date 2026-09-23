import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

DISCORD_API_URL = "https://discord.com/api/v10"


def _bot_token():
    token = getattr(settings, "DISCORD_BOT_TOKEN", None)
    if token:
        return token

    try:
        from aadiscordbot.app_settings import DISCORD_BOT_TOKEN
    except ImportError:
        return None
    return DISCORD_BOT_TOKEN


def get_guild_voice_states(guild_id):
    """Return voice state data supplied by the configured Discord integration."""
    try:
        from aadiscordbot import api as aadiscordbot_api
    except ImportError:
        aadiscordbot_api = None

    if aadiscordbot_api and hasattr(aadiscordbot_api, "get_guild_voice_states"):
        return aadiscordbot_api.get_guild_voice_states(guild_id) or []

    raise RuntimeError(
        "The configured Discord integration does not expose guild voice states. "
        "Enable the Alliance Auth Discord bot integration before taking snapshots."
    )


def sync_guild_channels(guild_id):
    """Fetch guild channels for future channel-management integrations."""
    token = _bot_token()
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN is not configured.")

    response = requests.get(
        f"{DISCORD_API_URL}/guilds/{guild_id}/channels",
        headers={"Authorization": f"Bot {token}"},
        timeout=15,
    )
    try:
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Discord channel synchronization failed")
        raise RuntimeError("Discord channel synchronization failed.") from None
    return response.json()

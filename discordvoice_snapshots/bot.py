import logging
from aadiscordbot.app_settings import DISCORD_BOT_TOKEN
from allianceauth.services.modules.discord.models import DiscordUser
from .models import Channel, Snapshot, SnapshotUser
from .utils import log_action

logger = logging.getLogger(__name__)

def handle_voice_state_update(data):
    """
    Called whenever Discord sends a VOICE_STATE_UPDATE event.
    """

    user_id = data.get("user_id")
    channel_id = data.get("channel_id")

    # User left voice
    if channel_id is None:
        logger.debug(f"User {user_id} left voice.")
        return

    du = DiscordUser.objects.filter(uid=user_id).first()
    if not du:
        logger.warning(f"VOICE_STATE_UPDATE: Unknown Discord user {user_id}")
        return

    aa_user = du.user

    channel_obj, _ = Channel.objects.get_or_create(
        name=str(channel_id),
        channel_type="voice"
    )

    snapshot = Snapshot.objects.create(channel=channel_obj)
    SnapshotUser.objects.get_or_create(snapshot=snapshot, user=aa_user)

    log_action(
        user=aa_user,
        action=f"Voice snapshot created in channel {channel_id}",
        old_value=None,
        new_value=f"Snapshot ID {snapshot.id}"
    )

    logger.info(f"Snapshot created for channel {channel_id} with user {aa_user.username}")

def discord_event_handler(event, data):
    if event == "VOICE_STATE_UPDATE":
        handle_voice_state_update(data)

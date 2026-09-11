import logging
from aadiscordbot.app_settings import DISCORD_BOT_TOKEN
from aadiscordbot.tasks import send_message
from allianceauth.services.modules.discord.models import DiscordUser
from .models import Channel, Snapshot, SnapshotUser

logger = logging.getLogger(__name__)


def handle_voice_state_update(data):
    """
    Called whenever Discord sends a VOICE_STATE_UPDATE event.
    `data` is the raw gateway payload from aadiscordbot.
    """

    user_id = data.get("user_id")
    channel_id = data.get("channel_id")

    # User left voice
    if channel_id is None:
        logger.debug(f"User {user_id} left voice.")
        return

    # Resolve DiscordUser → AA User
    du = DiscordUser.objects.filter(uid=user_id).first()
    if not du:
        logger.warning(f"VOICE_STATE_UPDATE: Unknown Discord user {user_id}")
        return

    aa_user = du.user

    # Create or get Channel record
    channel_obj, _ = Channel.objects.get_or_create(
        name=str(channel_id),
        channel_type="voice"
    )

    # Create snapshot
    snapshot = Snapshot.objects.create(channel=channel_obj)

    # Add user to snapshot
    SnapshotUser.objects.get_or_create(snapshot=snapshot, user=aa_user)

    logger.info(f"Snapshot created for channel {channel_id} with user {aa_user.username}")


# Hook into aadiscordbot event system
def discord_event_handler(event, data):
    if event == "VOICE_STATE_UPDATE":
        handle_voice_state_update(data)

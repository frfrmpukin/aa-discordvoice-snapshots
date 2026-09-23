import logging

from asgiref.sync import sync_to_async
from discord.ext import commands

from ..models import ActiveVoiceState

logger = logging.getLogger(__name__)


@sync_to_async
def _record_voice_state(guild_id, member_id, username, channel_id, channel_name):
    ActiveVoiceState.objects.update_or_create(
        guild_id=str(guild_id),
        discord_user_id=str(member_id),
        defaults={
            "discord_username": username or "",
            "channel_id": str(channel_id),
            "channel_name": channel_name or str(channel_id),
        },
    )


@sync_to_async
def _remove_voice_state(guild_id, member_id):
    ActiveVoiceState.objects.filter(
        guild_id=str(guild_id),
        discord_user_id=str(member_id),
    ).delete()


class VoiceSnapshotCog(commands.Cog):
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild_id = getattr(getattr(member, "guild", None), "id", None)
        if guild_id is None:
            return

        if after.channel is None:
            await _remove_voice_state(guild_id, member.id)
            return

        await _record_voice_state(
            guild_id,
            member.id,
            getattr(member, "display_name", None) or getattr(member, "name", ""),
            after.channel.id,
            getattr(after.channel, "name", str(after.channel.id)),
        )


def setup(bot):
    bot.add_cog(VoiceSnapshotCog(bot))

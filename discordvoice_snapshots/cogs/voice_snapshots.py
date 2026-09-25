import logging

from asgiref.sync import sync_to_async
from django.conf import settings
from discord.ext import commands

from ..models import ActiveVoiceState

logger = logging.getLogger(__name__)


@sync_to_async
def _sync_voice_states(guild_id, member_id, username, channel_id, channel_name):
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

        await _sync_voice_states(
            guild_id,
            member.id,
            getattr(member, "display_name", None) or getattr(member, "name", ""),
            after.channel.id,
            getattr(after.channel, "name", str(after.channel.id)),
        )

    @commands.Cog.listener()
    async def on_ready(self):
        configured_guild_id = getattr(settings, "DISCORD_GUILD_ID", None)
        if not configured_guild_id:
            logger.warning("DISCORD_GUILD_ID is not configured; skipping voice state synchronization.")
            return

        try:
            guild_id = int(configured_guild_id)
        except (TypeError, ValueError):
            logger.warning("DISCORD_GUILD_ID is invalid; skipping voice state synchronization.")
            return

        guild = self.bot.get_guild(guild_id)
        if guild is None:
            logger.warning("Discord guild %s is unavailable; skipping voice state synchronization.", guild_id)
            return

        synchronized_count = 0
        for member in guild.members:
            voice_state = getattr(member, "voice", None)
            channel = getattr(voice_state, "channel", None)
            if channel is None:
                continue

            await _sync_voice_states(
                guild_id,
                member.id,
                getattr(member, "display_name", None) or getattr(member, "name", ""),
                channel.id,
                getattr(channel, "name", str(channel.id)),
            )
            synchronized_count += 1

        logger.info(
            "Synchronized %s connected voice members for Discord guild %s.",
            synchronized_count,
            guild_id,
        )


def setup(bot):
    bot.add_cog(VoiceSnapshotCog(bot))

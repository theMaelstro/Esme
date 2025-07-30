"""Extension module for GuildList Cog."""
import logging

import discord
from discord.ext import tasks, commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import UniversalBuilder
from core import BaseCog

async def update_status_channel(channels: list[discord.VoiceChannel], channel_name, players):
    for channel in channels:
        if channel.name.split(":")[0] == channel_name:
            await channel.edit(name=f"{channel_name}: {players}")
            break

class PlayersOnlineTask(BaseCog):
    """Cog handling calculation of key flag."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.guild: discord.Guild = None
        self.universal_builder = UniversalBuilder()

    @tasks.loop(minutes=15)
    async def update_status_channels(self):
        """Display online players."""
        logging.info("Updating Player Online Status channels: %s.", self.__cog_name__)

        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            # Retrieve guilds.
            players_list = await self.universal_builder.get_players_online_per_land(session)

            # Close Session
            await session.commit()
            await session.close()

        category = discord.utils.get(
            self.guild.categories,
            id=CONFIG.discord.status_category_id
        )

        for server in players_list:
            await update_status_channel(
                category.channels,
                f"{server.world_name} {server.land}",
                server.current_players
            )

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Retrieving Guild: %s.", self.__cog_name__)
        self.guild = self.client.get_guild(CONFIG.discord.guild_id)
        logging.info("Starting Status task: %s.", self.__cog_name__)
        self.update_status_channels.start()

    async def cog_unload(self) -> None:
        self.update_status_channels.cancel()
        logging.info("Stopping Status task: %s.", self.__cog_name__)
        return await super().cog_unload()

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.guild_list.enabled:
        await client.add_cog(PlayersOnlineTask(client))

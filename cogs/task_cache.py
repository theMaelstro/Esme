"""Cache refresh module."""
import logging

from discord.ext import tasks, commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from core import BaseCog

from data.connector import CONN
from data.cache import (
    cache,
    GuildRecruitment,
    GuildCharacterDetails
)
from data import (
    CharactersBuilder,
    GuildBuilder
)

class CacheUpdate(BaseCog):
    """Cog handling calculation of key flag."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.guild_builder = GuildBuilder()
        self.characters_builder = CharactersBuilder()

    @tasks.loop(minutes=5)
    async def update_cache(self):
        """Update Cache variables."""
        logging.info("Updating Cache: %s.", self.__cog_name__)
        if not cache.guilds:
            # Create session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                guilds = await self.guild_builder.select_recruiting_guilds(session)
                guild_character_details = await self.characters_builder.select_characters_in_guild_details(session)

                # Close Session
                await session.commit()
                await session.close()
                cache.guilds = [
                    GuildRecruitment(
                        guild.guild_id,
                        guild.guild_name,
                        guild.leader_name,
                        guild.members
                    ) for guild in guilds
                ]
                cache.guild_character_details = [
                    GuildCharacterDetails(
                        detail.guild_id,
                        detail.discord_id,
                        detail.character_id,
                        detail.character_name,
                        detail.order_index,
                        detail.cid
                    ) for detail in guild_character_details
                ]

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Starting Cache task: %s.", self.__cog_name__)
        self.update_cache.start()

    async def cog_unload(self) -> None:
        self.update_cache.cancel()
        logging.info("Stopping Cache task: %s.", self.__cog_name__)
        return await super().cog_unload()

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(CacheUpdate(client))

"""Cache refresh module."""
import traceback
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
    DiscordBuilder,
    GuildBuilder
)

class CacheUpdate(BaseCog):
    """Cog handling calculation of key flag."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.character_builder = CharactersBuilder()
        self.discord_builder = DiscordBuilder()
        self.guild_builder = GuildBuilder()

    @tasks.loop(
        minutes=5,
        reconnect=True
    )
    async def update_cache(self):
        """Update Cache variables."""
        try:
            logging.info("Updating Cache: %s.", self.__cog_name__)
            # Create session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                guilds = await self.guild_builder.select_recruiting_guilds(session)
                guild_character_details = await self.character_builder.select_characters_in_guild_details(session)

                terms_sha = await self.discord_builder.select_meta(
                    session,
                    "terms"
                )
                terms_users = await self.discord_builder.get_terms_validated_users(
                    session
                )

                # Close Session
                await session.commit()
                await session.close()

                if isinstance(guilds, list):
                    cache.guilds = [
                        GuildRecruitment(
                            guild.guild_id,
                            guild.guild_name,
                            guild.leader_name,
                            guild.members
                        ) for guild in guilds
                    ]

                if isinstance(guild_character_details, list):
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

                if terms_sha is not None:
                    terms_sha = terms_sha['sha']
                if terms_sha is not None and isinstance(terms_users, list):
                    cache.terms_accepted = set((
                        user.discord_id for user in terms_users if user.terms == terms_sha
                    ))

            logging.info("Cache Updated: %s.", self.__cog_name__)

        except (
            Exception
        ) as e:
            logging.error("Cache update failed: %s %s %s", type(e), e, traceback.format_exc())

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

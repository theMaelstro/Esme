"""Extension module for GuildList Cog."""
from typing import List
import re
import logging

import discord
from discord.app_commands import Choice
from sqlalchemy.ext.asyncio import async_sessionmaker

from data.connector import CONN
from data.cache import cache
from data import (
    CharactersBuilder,
    DiscordBuilder,
    GuildBuilder
)
from core.exceptions import (
    CoroutineFailed,
    CharacterNotSet,
    CharacterAlreadyInGuild,
    DiscordNotRegistered,
    GuildAlreadyApplied,
    GuildFull,
    GuildNameInvalid
)
from core import max_members

def validate_guild(name: str):
    """Check if guild is in cached list."""
    for guild in cache.guilds:
        if name == guild.name:
            return guild.gid
    return False

class GuildApply():
    """Cog handling applying to guild."""
    def __init__(self):
        self.character_builder = CharactersBuilder()
        self.discord_builder = DiscordBuilder()
        self.guild_builder = GuildBuilder()

    async def guild_apply(
        self,
        interaction: discord.Interaction,
        guild_name: str
    ):
        """Show all guilds."""
        try:
            guild_id = validate_guild(guild_name)
            if not guild_id:
                raise GuildNameInvalid(
                    """Guild Name is invalid."""
                )

            # Start session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                # Check if sender is registered.
                discord_user = await self.discord_builder.select_discord_user(
                    session, str(interaction.user.id)
                )
                if discord_user is None:
                    raise DiscordNotRegistered(
                        "No account registered for this discord user."
                )

                if discord_user.character_id is None:
                    raise CharacterNotSet(
                        "No character selected. Please use `/account character select` command."
                    )

                character = await self.guild_builder.select_guild_character_details_by_character_id(
                    session,
                    discord_user.character_id
                )

                if character:
                    raise CharacterAlreadyInGuild(
                        "Character already in guild"
                    )

                guild = await self.guild_builder.select_recruiting_guild_by_id(session, guild_id)
                if guild.members >= max_members(guild.guild_rp):
                    raise GuildFull(
                        "Guild is full and cannot accept new members."
                    )

                application = await self.guild_builder.check_guild_application(
                    session,
                    discord_user.character_id,
                    guild_id
                )
                if application:
                    raise GuildAlreadyApplied(
                        f"Character already applied to {guild_name} guild."
                    )

                await self.guild_builder.insert_guild_application(
                    session,
                    guild_id,
                    discord_user.character_id,
                    discord_user.character_id,
                    "applied"
                )

                # Close Session
                await session.commit()
                await session.close()

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Application Sent",
                    description=guild_name,
                    color=discord.Color.green()
                ),
                ephemeral=True
            )

        except (
            DiscordNotRegistered,
            CharacterNotSet,
            CharacterAlreadyInGuild,
            GuildAlreadyApplied,
            GuildFull,
            GuildNameInvalid
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Guild Apply Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    async def guild_apply_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[Choice[str]]:
        """Autocomplete callback function."""
        try:
            if len(current) > 0:
                return [
                    Choice(
                        name=f"{str(guild.members).zfill(2)} | {guild.name}",
                        value=guild.name
                    ) for guild in cache.guilds
                    if current.lower() in guild.name.lower()
                ][:10]

            return [
                Choice(
                    name=f"{str(guild.members).zfill(2)} | {guild.name}",
                    value=guild.name
                ) for guild in cache.guilds
            ][:10]

        except (
            CoroutineFailed
        ) as e:
            logging.error("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Guild List Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        except (
            Exception
        ) as e:
            logging.error("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Guild List Failed",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

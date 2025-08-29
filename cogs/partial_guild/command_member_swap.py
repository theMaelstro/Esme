"""Extension module for Guild Cog."""
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

from settings import CONFIG
from core.exceptions import (
    CoroutineFailed,
    CharacterNameInvalid,
    CharacterNotInGuild,
    CharacterNotSet,
    CharactersAreEqual,
    CharacterIsLeader,
    DiscordNotRegistered,
    MissingPermissions
)

def validate_character(name: str):
    """Check if character is in cached list."""
    for character in cache.guild_character_details:
        if name == character.character_name:
            return character.character_id
    return False

def get_cache_character(discord_id: str):
    """Get character from cache."""
    for character in cache.guild_character_details:
        if character.discord_id == discord_id and character.character_id == character.selected:
            return character
    return None

class MemberSwap():
    """Cog handling expelling guild members."""
    def __init__(self):
        self.character_builder = CharactersBuilder()
        self.discord_builder = DiscordBuilder()
        self.guild_builder = GuildBuilder()

    async def guild_swap(
        self,
        interaction: discord.Interaction,
        character_name_1: str,
        character_name_2: str
    ):
        """Expel guild member."""
        try:
            if not CONFIG.check_permission(
                CONFIG.commands.guild_members_swap.permission,
                interaction.user
            ):
                raise MissingPermissions(
                    f"{interaction.user.mention} is missing permissions to use command."
                )

            character_id_1 = validate_character(character_name_1)
            if not character_id_1:
                raise CharacterNameInvalid(
                    """Character Name is invalid."""
                )

            character_id_2 = validate_character(character_name_2)
            if not character_id_2:
                raise CharacterNameInvalid(
                    """Character Name is invalid."""
                )

            if character_id_1 == character_id_2:
                raise CharactersAreEqual(
                    """Characters cannot be swapped."""
                )

            # Start session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
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

                if not character:
                    raise CharacterNotInGuild(
                        "Character is not a Guild member."
                    )

                if character.order_index != 1:
                    raise MissingPermissions(
                        "No valid candidate to replace guild leader."
                    )

                character_1 = await self.guild_builder.select_guild_character_details_by_character_id(
                    session,
                    character_id_1
                )

                character_2 = await self.guild_builder.select_guild_character_details_by_character_id(
                    session,
                    character_id_2
                )

                if character_1.order_index == 1 or character_2.order_index == 1:
                    raise CharacterIsLeader(
                        "Cannot reorder guild leader."
                    )

                if not await self.guild_builder.update_guild_member_position(
                    session,
                    character_id_1,
                    character_2.order_index
                ):
                    raise CoroutineFailed(
                        "Could not update character guild position."
                    )

                if not await self.guild_builder.update_guild_member_position(
                    session,
                    character_id_2,
                    character_1.order_index
                ):
                    raise CoroutineFailed(
                        "Could not update character guild position."
                    )

                # Close Session
                await session.commit()
                await session.close()

            logging.info(
                "Members Swapped: %s %s %s",
                interaction.user.id,
                character_name_1,
                character_name_2
            )
            await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Members Swapped",
                        description=(
                            f"`{character_name_1}` ↔️ `{character_name_2}`\n"
                            "### Before\n"
                            f"{character_1.order_index}|`{character_name_1}`\n"
                            f"{character_2.order_index}|`{character_name_2}`\n"
                            "### After\n"
                            f"{character_1.order_index}|`{character_name_2}`\n"
                            f"{character_2.order_index}|`{character_name_1}`\n"
                            "Check results with `/guild members list`"
                        ),
                        color=discord.Color.green()
                    ),
                    ephemeral=True
                )

        except (
            CharacterIsLeader,
            CharacterNameInvalid,
            CharacterNotInGuild,
            CharacterNotSet,
            CharactersAreEqual,
            DiscordNotRegistered,
            MissingPermissions
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Guild Expel Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        except (
            CoroutineFailed
        ) as e:
            logging.error("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Guild Expel Failed",
                    description="Internal Error",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    async def guild_swap_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[Choice[str]]:
        """Autocomplete callback function."""
        try:
            guild = get_cache_character(str(interaction.user.id))
            if guild:
                if len(current) > 0:
                    if guild.order_index == 1:
                        return [
                            Choice(
                                name=f"{str(value.order_index).zfill(2)} | {value.character_name}",
                                value=value.character_name
                            ) for value in cache.guild_character_details
                            if current.lower() in value.character_name.lower()
                            and value.guild_id == guild.guild_id
                        ][:10]
                return [
                    Choice(
                        name="Start typing to find members...",
                        value="Start typing to find members..."
                    )
                ]
            return [
                    Choice(
                        name="You are not in guild...",
                        value="You are not in guild..."
                    )
                ]

        except (
            CoroutineFailed
        ) as e:
            logging.error("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Guild Expel Failed",
                    description="Internal Error",
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
                    title="Guild Expel Failed",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

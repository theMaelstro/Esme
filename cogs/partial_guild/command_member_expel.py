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
    DiscordNotRegistered,
    GuildLeaderCandidateMissing,
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

class MemberExpel():
    """Cog handling expelling guild members."""
    def __init__(self):
        self.character_builder = CharactersBuilder()
        self.discord_builder = DiscordBuilder()
        self.guild_builder = GuildBuilder()

    async def guild_expel(
        self,
        interaction: discord.Interaction,
        character_name: str
    ):
        """Expel guild member."""
        try:
            if not CONFIG.check_permission(
                CONFIG.commands.guild_members_expel.permission,
                interaction.user
            ):
                raise MissingPermissions(
                    f"{interaction.user.mention} is missing permissions to use command."
                )

            character_id = validate_character(character_name)
            if not character_id:
                raise CharacterNameInvalid(
                    """Character Name is invalid."""
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

                if discord_user.character_id == character_id:
                    if character.order_index == 1:
                        leader_candidate = await self.guild_builder.select_leader_candidate_by_guild_id(
                            session,
                            character.guild_id
                        )
                        if not leader_candidate:
                            raise GuildLeaderCandidateMissing(
                                "No valid candidate to replace guild leader."
                            )

                        if not await self.guild_builder.update_guild_leader(
                            session,
                            leader_candidate.guild_id,
                            leader_candidate.character_id
                        ):
                            raise CoroutineFailed(
                                "Could not update character guild leader."
                            )

                        await self.guild_builder.delete_guild_character(
                            session,
                            discord_user.character_id
                        )

                        if not await self.guild_builder.update_guild_member_position(
                            session,
                            leader_candidate.character_id,
                            1
                        ):
                            raise CoroutineFailed(
                                "Could not update character guild position."
                            )

                        await self.character_builder.insert_message(
                            session,
                            sender_id = 0,
                            recipient_id = discord_user.character_id,
                            subject = "Withdrawal",
                            body = (
                                f"You have withdrawn from 「{character.guild_name}」.\n"
                                f"Ownership transferred to 「{leader_candidate.character_name}」."
                            ),
                            is_guild_invite=False
                        )

                        await self.character_builder.insert_message(
                            session,
                            sender_id = 0,
                            recipient_id = leader_candidate.character_id,
                            subject = "Leadership",
                            body = (
                                f"Leader 「{character.character_name}」 withdrawn.\n"
                                f"You have been awarded ownership\n"
                                f"of 「{character.guild_name}」 guild."
                            ),
                            is_guild_invite=False
                        )

                    else:
                        if not await self.guild_builder.select_guild_character_details_by_character_id(
                            session,
                            character_id
                        ):
                            raise CharacterNotInGuild(
                                "Character cannot be expelled. Not member of guild."
                            )

                        await self.guild_builder.delete_guild_character(
                            session,
                            discord_user.character_id
                        )
                        await self.character_builder.insert_message(
                            session,
                            sender_id = 0,
                            recipient_id = discord_user.character_id,
                            subject = "Withdrawal",
                            body = (
                                f"You have withdrawn from 「{character.guild_name}」."
                            ),
                            is_guild_invite=False
                        )

                else:
                    if character.order_index != 1:
                        raise MissingPermissions(
                            "Character is not a guild leader."
                        )

                    await self.guild_builder.delete_guild_character(session, character_id)
                    await self.character_builder.insert_message(
                        session,
                        sender_id = discord_user.character_id,
                        recipient_id = character_id,
                        subject = "Kicked",
                        body = f"You were kicked from 「{character.guild_name}」.",
                        is_guild_invite=False
                    )

                # Close Session
                await session.commit()
                await session.close()

            logging.info("Member Expelled: %s %s", interaction.user.id, character_name)
            await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Member Expelled",
                        description=f"`{character_name}` has been expelled from `{character.guild_name}`",
                        color=discord.Color.green()
                    ),
                    ephemeral=True
                )

        except (
            CharacterNameInvalid,
            CharacterNotInGuild,
            CharacterNotInGuild,
            CharacterNotSet,
            DiscordNotRegistered,
            GuildLeaderCandidateMissing,
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

    async def guild_expel_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[Choice[str]]:
        """Autocomplete callback function."""
        try:
            character = get_cache_character(str(interaction.user.id))
            if character:
                if len(current) > 0:
                    if character.order_index == 1:
                        return [
                            Choice(
                                name=f"{str(value.order_index).zfill(2)} | {value.character_name}",
                                value=value.character_name
                            ) for value in cache.guild_character_details
                            if current.lower() in value.character_name.lower()
                            and value.guild_id == character.guild_id
                        ][:10]
                    return [
                        Choice(
                            name=f"{str(value.order_index).zfill(2)} | {value.character_name}",
                            value=value.character_name
                        ) for value in cache.guild_character_details
                        if character.character_name == value.character_name
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

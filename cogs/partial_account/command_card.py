"""Extension module for AccountCard Cog."""
import re
import logging

import discord
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import (
    CharactersBuilder,
    DiscordBuilder
)
from core import get_weapon_type_image_url
from core.exceptions import (
    CoroutineFailed,
    CharacterNotSet,
    DiscordNotRegistered
)

class Card():
    """
    Cog handling active character card.
    """
    def __init__(self):
        self.character_builder = CharactersBuilder()
        self.discord_builder = DiscordBuilder()

    async def card(self, interaction: discord.Interaction, member: discord.Member):
        """Select active character."""
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            try:
                # Check if user is registered.
                discord_user = await self.discord_builder.select_discord_user(
                    session, str(interaction.user.id) if not member else str(member.id)
                )
                if discord_user is None:
                    raise DiscordNotRegistered(
                        "No account registered for this discord user."
                    )

                # Get character list.
                character = await self.character_builder.select_character_details_by_character_id(
                    session,
                    discord_user.character_id
                )
                if character is None:
                    raise CharacterNotSet(
                        "No character selected. Please use `/account character select` command."
                    )

                elevated = (
                    interaction.user.id in CONFIG.discord.admin_user_ids
                    or interaction.user.id == member.id
                )

                # Prepare embed
                embed=discord.Embed(
                    title=
                        (
                            f'{character.uid} | {character.character_id} | '
                            if interaction.user.id in CONFIG.discord.admin_user_ids
                            else ''
                        ) + re.escape(character.character_name),
                    description='',
                    color=discord.Color.blue()
                )

                if character.guild_name:
                    embed.description += (
                        f'**{character.guild_id} |** '
                            if interaction.user.id in CONFIG.discord.admin_user_ids
                            else ''
                    ) + f"**{re.escape(character.guild_name)}**"
                    embed.description += f"\nmember since\n<t:{round(character.joined_at_epoch)}:d>"

                if elevated and character.psn_id:
                    embed.description += f"\n\n**PSN**: `{re.escape(character.psn_id)}`"

                if character.gr > 0:
                    embed.add_field(
                        name = 'GR',
                        value = character.gr,
                        inline = True
                    )
                else:
                    embed.add_field(
                        name = 'HR',
                        value = character.hr,
                        inline = True
                    )

                if elevated:
                    embed.add_field(
                        name = 'LAST LOGIN',
                        value = f"<t:{character.last_login}:f>",
                        inline = False
                    )
                    embed.add_field(
                        name = 'KP',
                        value = character.kouryou_point,
                        inline = True
                    )
                    embed.add_field(
                        name = 'GCP',
                        value = character.gcp,
                        inline = True
                    )
                    embed.add_field(
                        name = 'NP',
                        value = character.netcafe_points,
                        inline = True
                    )

                embed.set_thumbnail(url=get_weapon_type_image_url(character.weapon_type))
                if member:
                    embed.set_author(
                        name=f"{member}",
                        icon_url=member.avatar.url
                    )
                else:
                    embed.set_author(
                        name=f"{interaction.user}",
                        icon_url=interaction.user.avatar.url
                    )

                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True
                )

            except (
                DiscordNotRegistered,
                CharacterNotSet
            ) as e:
                logging.warning("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Card Failed",
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
                        title="Card Failed",
                        description=e,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

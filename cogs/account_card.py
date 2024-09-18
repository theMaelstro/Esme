"""Extension module for AccountCard Cog."""
import re
import logging

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import CharactersBuilder
from data import DiscordBuilder
from core import get_weapon_type_image_url
from core.exceptions import (
    CoroutineFailed,
    DiscordNotRegistered
)
from core import BaseCog

class AccountCard(BaseCog):
    """
    Cog handling active character card.
    """
    def __init__(self, client: commands.Bot):
        self.client = client
        self.characters_builder = CharactersBuilder()
        self.discord_builder = DiscordBuilder()

    @app_commands.command(
        name="card",
        description="Show active character card."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.account_card.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def account_card(self, interaction: discord.Interaction):
        """Select active character."""
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            try:
                # Check if user is registered.
                discord_user = await self.discord_builder.select_discord_user(
                    session, str(interaction.user.id)
                )
                if discord_user is None:
                    raise DiscordNotRegistered(
                        "No account registered for this discord user."
                    )

                # Get character list.
                character = await self.characters_builder.select_character_by_id(
                    session,
                    discord_user.user_id
                )
                if character is None:
                    raise CoroutineFailed(
                        "Query did not yield valid results."
                    )

                # Prepare embed
                embed=discord.Embed(
                    title=re.escape(character.name),
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name = 'ID',
                    value = character.id,
                    inline = True
                )
                embed.add_field(
                    name = 'HR',
                    value = character.hrp,
                    inline = True
                )
                embed.add_field(
                    name = 'GR',
                    value = character.gr,
                    inline = True
                )
                embed.add_field(
                    name = 'LAST LOGIN',
                    value = f"<t:{round(character.last_login)}:f>",
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
                embed.set_author(
                    name=f"{interaction.user}",
                    icon_url=interaction.user.avatar.url
                )
                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True
                )

            except (
                DiscordNotRegistered
            ) as e:
                logging.warning("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Character Select Failed",
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
                        title="Character Select Failed",
                        description=e,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

    @account_card.error
    async def on_account_card_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.character_select.enabled:
        await client.add_cog(AccountCard(client))

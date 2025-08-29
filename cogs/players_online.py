"""Extension module for GuildList Cog."""
import logging

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import UniversalBuilder
from core import BaseCog
from core.exceptions import (
    CoroutineFailed,
    MissingPermissions
)

class PlayersOnline(BaseCog):
    """Cog handling calculation of key flag."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.universal_builder = UniversalBuilder()

    @app_commands.command(
        name="players",
        description="Show online players per server."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.players_online.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def players_online(
        self,
        interaction: discord.Interaction
    ):
        """Display online players."""
        try:
            if not CONFIG.check_permission(
                CONFIG.commands.players_online.permission,
                interaction.user
            ):
                raise MissingPermissions(
                    f"{interaction.user.mention} is missing permissions."
                )
            # Create session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                # Retrieve guilds.
                players_list = await self.universal_builder.get_players_online_per_land(session)

                # Close Session
                await session.commit()
                await session.close()

            if not isinstance(players_list, list):
                raise CoroutineFailed(
                    "Query did not yield valid results."
                )
            desc = ""
            for element in players_list:
                desc += f"**{element.world_name} {element.land}**:   `{element.current_players}`\n"
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Players Online",
                    description=desc,
                    color=discord.Color.green()
                ),
                ephemeral=True
            )
        except (
            MissingPermissions
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Players Online Failed",
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
                    title="Online Players Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @players_online.error
    async def on_players_online_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.players_online.enabled:
        await client.add_cog(PlayersOnline(client))

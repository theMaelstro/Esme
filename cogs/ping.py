"""Extension module for example Ping Cog with response interaction."""
import logging

import discord
from discord.ext import commands
from discord import app_commands

from settings import CONFIG
from core import BaseCog
from core.exceptions import (
     MissingPermissions
)

class Ping(BaseCog):
    """Cog example with basic interaction response."""
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(
        name="ping",
        description="Ping!"
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.ping.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def ping(self, interaction: discord.Interaction):
        """Ping!"""
        try:
            if not CONFIG.check_permission(
                CONFIG.commands.ping.permission,
                interaction.user
            ):
                raise MissingPermissions(
                    f"{interaction.user.mention} is missing permissions to use command."
                )
            logging.info("%s: %s", interaction.user.id, "Ping!")
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Pong!",
                    description=(
                        "# Pong"
                        f"{interaction.user.mention}"
                    ),
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

    @ping.error
    async def on_ping_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.ping.enabled:
        await client.add_cog(Ping(client))

"""Extension module for example Ping Cog with response interaction."""
import logging

import discord
from discord.ext import commands
from discord import app_commands

from settings import CONFIG
from core import BaseCog

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
        CONFIG.commands.realm.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def ping(self, interaction: discord.Interaction):
        """Ping!"""
        logging.error("%s: %s", interaction.user.id, "Ping!")
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Pong!",
                description=(
                    "# [Pong](https://tenor.com/view/asby-vtuber-streamer-steering-wheel-swerving-gif-27623108)\n"
                    f"{interaction.user.mention}"
                ),
                color=discord.Color.green()
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
    await client.add_cog(Ping(client))

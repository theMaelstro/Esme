import time

import discord
from discord.ext import commands
from discord import app_commands
from settings import CONFIG

class Ping(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="ping", description="Ping!")
    @app_commands.checks.cooldown(
    1,
    CONFIG.commands.realm.cooldown,
    key=lambda i: (i.guild_id, i.user.id)
    )
    async def ping(self, interaction: discord.Interaction):
        """Ping!"""
        await interaction.response.send_message(
            f'# [Pong](https://tenor.com/view/asby-vtuber-streamer-steering-wheel-swerving-gif-27623108)\n{interaction.user.mention}',
            ephemeral=True)

    @ping.error
    async def on_ping_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        if isinstance(error, app_commands.CommandOnCooldown):
            remaining_time = round(error.retry_after)
            await interaction.response.send_message(
                f"You are on cooldown. Please try again <t:{round(time.time())+remaining_time}:R>",
                ephemeral=True
            )

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(Ping(client))

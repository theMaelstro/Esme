import time

import discord
from discord.ext import commands
from discord import app_commands

from settings import CONFIG
import core.viewmodel as view

class UpdateGuild(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.viewmodel = view.View()

    @app_commands.command(name="update_guild", description="Ping!")
    @app_commands.checks.cooldown(
    1,
    CONFIG.commands.realm.cooldown,
    key=lambda i: (i.guild_id, i.user.id)
    )
    async def update_guild(self, interaction: discord.Interaction, guild_id: int, leader_id: int):
        """Current realm list setting."""
        await self.viewmodel.update_guild_leader(guild_id, leader_id)
        await interaction.response.send_message(
            f'Beep Boop {interaction.user.mention}',
            ephemeral=True
        )

    @update_guild.error
    async def on_update_guild_error(
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
    await client.add_cog(UpdateGuild(client))

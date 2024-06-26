"""
Module which contains Base Cog Class.
"""
import time
import logging

from discord.ext import commands
import discord
from discord import app_commands

class BaseCog(commands.Cog):
    """
    Custom base class for Cogs.

    Implements loading and unloading logging.
    """
    async def cog_load(self) -> None:
        logging.info("Cog Loaded: %s.", self.__cog_name__)
        return await super().cog_load()

    async def cog_unload(self) -> None:
        logging.info("Cog Unloaded: %s.", self.__cog_name__)
        return await super().cog_unload()

    async def on_cooldown_response(
            self,
            interaction: discord.Interaction,
            error:app_commands.AppCommandError
    ) -> None:
        """Respond with embed on cooldown error."""
        if isinstance(error, app_commands.CommandOnCooldown):
            remaining_time = round(error.retry_after)
            logging.info("%s: %s", interaction.user.id, "Cooldown not expired")
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Binding Failed",
                    description=(
                        "You are on cooldown. Please try again "
                        f"<t:{round(time.time())+remaining_time}:R>"
                    ),
                    color=discord.Color.blue()
                ),
                ephemeral=True
            )

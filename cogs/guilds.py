import time
import re

import discord
from discord.ext import commands
from discord import app_commands

from settings import CONFIG
import core.viewmodel as view
from core.view.pagination import Pagination

class Guilds(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.viewmodel = view.View()

    @app_commands.command(name="guilds", description="Show all guilds.")
    @app_commands.checks.cooldown(
    1,
    CONFIG.commands.realm.cooldown,
    key=lambda i: (i.guild_id, i.user.id)
    )
    async def guilds(self, interaction: discord.Interaction):
        """Current realm list setting."""
        elements = await self.viewmodel.select_guilds()
        if isinstance(elements, list):
            L = 15
            async def get_page(page: int):
                emb = discord.Embed(title="Guild List", description="", color=0x1E90FF)
                offset = (page-1) * L
                for guild in elements[offset:offset+L]:
                    emb.description += (
                        f"**{guild.id}**: {re.escape(guild.name)}\n"
                    )
                emb.set_author(
                    name=f"Requested by {interaction.user}",
                    icon_url=interaction.user.avatar.url
                )
                n = Pagination.compute_total_pages(len(elements), L)
                emb.set_footer(text=f"Page {page} from {n}")
                return emb, n

            await Pagination(interaction, get_page, public=False).navegate()
        else:
            await interaction.response.send_message("Error", ephemeral=True)

    @guilds.error
    async def on_guilds_error(
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
    await client.add_cog(Guilds(client))

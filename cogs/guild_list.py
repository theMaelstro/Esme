import time
import re

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import GuildBuilder
from core.view.pagination import Pagination

class GuildList(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.viewmodel = GuildBuilder()

    @app_commands.command(name="guild_list", description="Show all guilds.")
    @app_commands.checks.cooldown(
    1,
    CONFIG.commands.realm.cooldown,
    key=lambda i: (i.guild_id, i.user.id)
    )
    async def guild_list(self, interaction: discord.Interaction):
        """Show all guilds."""
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            # Retrieve guilds.
            elements = await self.viewmodel.select_guilds(session)

            # Close Session
            await session.commit()
            await session.close()

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

    @guild_list.error
    async def on_guild_list_error(
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
    await client.add_cog(GuildList(client))

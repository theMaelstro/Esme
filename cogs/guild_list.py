"""Extension module for GuildList Cog."""
import re
import logging

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import GuildBuilder
from core.view.pagination import Pagination
from core import BaseCog
from core.exceptions import CoroutineFailed

class GuildList(BaseCog):
    """Cog handling displaying of guilds in a list."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.guild_builder = GuildBuilder()

    @app_commands.command(
        name="guild_list",
        description="Show all guilds."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.guild_list.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def guild_list(self, interaction: discord.Interaction):
        """Show all guilds."""
        try:
            # Create session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                # Retrieve guilds.
                elements = await self.guild_builder.select_guilds(session)

                # Close Session
                await session.commit()
                await session.close()

            if not isinstance(elements, list):
                raise CoroutineFailed(
                    "Query did not yield valid results."
                )

            page_elements = 15
            async def get_page(page: int):
                emb = discord.Embed(title="Guild List", description="", color=discord.Color.green())
                offset = (page-1) * page_elements
                for guild in elements[offset:offset+page_elements]:
                    emb.description += (
                        f"**{guild.id}**: {re.escape(guild.name)}\n"
                    )

                emb.set_author(
                    name=f"Requested by {interaction.user}",
                    icon_url=interaction.user.avatar.url
                )
                n = Pagination.compute_total_pages(len(elements), page_elements)
                emb.set_footer(text=f"Page {page} from {n}")
                return emb, n

            logging.info("%s: %s", interaction.user.id, "Guild List Open")
            await Pagination(interaction, get_page, public=False).navegate()

        except (
            CoroutineFailed
        ) as e:
            logging.error("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Guild List Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @guild_list.error
    async def on_guild_list_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.guild_list.enabled:
        await client.add_cog(GuildList(client))

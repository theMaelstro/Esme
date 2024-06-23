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

class GuildMembers(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.viewmodel = GuildBuilder()

    @app_commands.command(name="guild_members", description="Show all guilds.")
    @app_commands.describe(
    guild_id='Guild id to list members from.',
    )
    @app_commands.checks.cooldown(
    1,
    CONFIG.commands.realm.cooldown,
    key=lambda i: (i.guild_id, i.user.id)
    )
    async def guild_members(self, interaction: discord.Interaction, guild_id: int):
        """Show all guilds."""
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            elements = await self.viewmodel.select_guild_characters_by_guild_id(session, guild_id)

            # Close Session
            await session.commit()
            await session.close()

        if isinstance(elements, list):
            L = 15
            async def get_page(page: int):
                emb = discord.Embed(title="Guild Members", description="", color=0x1E90FF)
                offset = (page-1) * L
                for member in elements[offset:offset+L]:
                    emb.description += (
                        f"**{member.id}**: {re.escape(member.name)} | <t:{round(member.joined_at_epoch)}:f>\n"
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

    @guild_members.error
    async def on_guild_members_error(
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
    await client.add_cog(GuildMembers(client))

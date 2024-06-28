"""Extension module for GuildMembers Cog."""
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

class GuildMembers(BaseCog):
    """Cog handling displaying of guild members in a list."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.guild_builder = GuildBuilder()

    @app_commands.command(
        name="guild_members",
        description="Show all guilds."
    )
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
        try:
            # Create session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                elements = await self.guild_builder.select_guild_characters_by_guild_id(
                    session,
                    guild_id
                )
                guild = await self.guild_builder.select_guild(
                    session,
                    guild_id
                )

                # Close Session
                await session.commit()
                await session.close()

            if not isinstance(elements, list):
                raise CoroutineFailed(
                    "Query did not yield valid results."
                )

            page_elements = 7
            async def get_page(page: int):
                emb = discord.Embed(
                    title="Guild Members",
                    description="",
                    color=discord.Color.green()
                )
                emb.add_field(
                    name="",
                    value="",
                    inline=True
                )
                emb.add_field(
                    name="NAME",
                    value="",
                    inline=True
                )
                emb.add_field(
                    name="JOINED",
                    value="",
                    inline=True
                )

                offset = (page-1) * page_elements
                for member in elements[offset:offset+page_elements]:
                    emb.add_field(
                        name="",
                        value=member.order_index,
                        inline=True
                    )
                    emb.add_field(
                        name="",
                        value=re.escape(member.name),
                        inline=True
                    )
                    emb.add_field(
                        name="",
                        value=f"<t:{round(member.joined_at_epoch)}:f>",
                        inline=True
                    )
                emb.set_author(
                    name=re.escape(guild.name)
                )
                n = Pagination.compute_total_pages(len(elements), page_elements)
                emb.set_footer(text=f"Page {page} from {n}")
                return emb, n

            logging.info("%s: %s", interaction.user.id, "Guild Members Open")
            await Pagination(interaction, get_page, public=False).navegate()

        except (
            CoroutineFailed
        ) as e:
            logging.error("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Guild Members Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @guild_members.error
    async def on_guild_members_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(GuildMembers(client))

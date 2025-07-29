"""Extension module for GuildMembers Cog."""
import re
import logging

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import (
    DiscordBuilder,
    GuildBuilder
)
from core.view.pagination import Pagination
from core import BaseCog
from core.exceptions import (
    CoroutineFailed,
    DiscordNotRegistered,
    InvalidArgument,
    MissingPermissions,
    CharacterNotInGuild,
    MissingGuildApplications
)

class MembersList():
    """Holder for members list command."""
    def __init__(self):
        self.discord_builder = DiscordBuilder()
        self.guild_builder = GuildBuilder()

    async def guild_members(self, interaction: discord.Interaction):
        """Show all guilds."""
        try:
            # Start session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                # Check if user is registered.
                discord_user = await self.discord_builder.select_discord_user(
                    session, str(interaction.user.id)
                )
                if discord_user is None:
                    raise DiscordNotRegistered(
                        "No account registered for this discord user."
                )

                guild_character = await self.guild_builder.select_guild_character_by_character_id(
                    session, discord_user.character_id
                )

                if guild_character is None:
                    raise CharacterNotInGuild(
                        "Character is not a Guild member."
                    )

                elements = await self.guild_builder.select_guild_characters_by_guild_id(
                    session,
                    guild_character.guild_id
                )
                guild = await self.guild_builder.select_guild(
                    session,
                    guild_character.guild_id
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
                        value=re.escape(member.character_name),
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

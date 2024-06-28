"""Extension module for GuildSetLeader Cog."""
import logging

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import GuildBuilder
from core import BaseCog
from core import (
    CoroutineFailed,
    MissingPermissions
)

class GuildSetLeader(BaseCog):
    """Cog handling guild leader update by admin."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.guild_builder = GuildBuilder()

    @app_commands.command(
        name="guild_set_leader",
        description="Set guild leader by id."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.realm.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def guild_set_leader(
        self,
        interaction: discord.Interaction,
        guild_id: int,
        leader_id: int
    ):
        """Set guild leader by id."""
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            try:
                if interaction.author.id not in CONFIG.discord.admin_user_ids:
                    raise MissingPermissions(
                        f"{interaction.author.mention} is missing permissions."
                    )

                if not await self.guild_builder.update_guild_leader(
                    self,
                    guild_id,
                    leader_id
                ):
                    raise CoroutineFailed(
                        "Could not update table."
                    )

                # Commit Session
                await session.commit()

                logging.info("%s: %s", interaction.user.id, "Leader Updated")
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Leader Updated",
                        color=discord.Color.green()
                    ),
                    ephemeral=True
                )

            except (
                MissingPermissions
            ) as e:
                logging.warning("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Leader Update Failed",
                        description=e,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

            except (
                CoroutineFailed
            ) as e:
                logging.error("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Leader Update Failed",
                        description=e,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

            finally:
                # Close session
                await session.close()

    @guild_set_leader.error
    async def on_guild_set_leader_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(GuildSetLeader(client))

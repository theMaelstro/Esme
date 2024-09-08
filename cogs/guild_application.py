"""Extension module for GuildApplication Cog."""
import logging
from typing import Literal

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
from core import BaseCog
from core.exceptions import (
    CoroutineFailed,
    DiscordNotRegistered,
    InvalidArgument,
    MissingPermissions
)

class GuildApplication(BaseCog):
    """Cog handling guild applications."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.discord_builder = DiscordBuilder()
        self.guild_builder = GuildBuilder()

    @app_commands.command(
        name="guild_application",
        description="Manage guild application by id."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.guild_application.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def guild_application(
        self,
        interaction: discord.Interaction,
        application_id: int,
        decision: Literal["accept", "decline"]
    ):
        """Manage guild application by id."""
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

                # Check if user is eleveated guild member.
                guild_application = await self.guild_builder.select_guild_application_by_id(
                    session,
                    application_id
                )
                if guild_application is None:
                    raise InvalidArgument(
                        "Invalid application id."
                    )
                discord_ids = await self.guild_builder.select_recruiter_discord_ids(
                    session,
                    guild_application.guild_id
                )
                if str(interaction.user.id) not in discord_ids:
                    raise MissingPermissions(
                        "You are not elevated guild member."
                    )

                match decision:
                    # On application accepted.
                    case "accept":
                        await self.guild_builder.insert_guild_member(
                            session,
                            guild_application.guild_id,
                            guild_application.character_id
                        )
                        await self.guild_builder.delete_guild_application(
                            session,
                            guild_application.id
                        )

                        await interaction.response.send_message(
                            embed=discord.Embed(
                                title=f"Application `{application_id}`",
                                description="Accepted",
                                color=discord.Color.blue()
                            ),
                            ephemeral=True
                        )
                    # On application declined.
                    case "decline":
                        await self.guild_builder.delete_guild_application(
                            session,
                            guild_application.id
                        )

                        await interaction.response.send_message(
                            embed=discord.Embed(
                                title=f"Application `{application_id}`",
                                description="Declined",
                                color=discord.Color.blue()
                            ),
                            ephemeral=True
                        )
                    case _:
                        raise CoroutineFailed(
                            "Unhandled Exception."
                        )

                # Close Session
                await session.commit()
                await session.close()

        except (
            DiscordNotRegistered,
            InvalidArgument,
            MissingPermissions
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Application Process Failed",
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
                    title="Application Process Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @guild_application.error
    async def on_guild_application_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.guild_set_leader.enabled:
        await client.add_cog(GuildApplication(client))

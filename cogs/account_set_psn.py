"""Extension module for SetPsn Cog."""
import logging

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import UserBuilder, DiscordBuilder
from core.exceptions import (
    CoroutineFailed,
    DiscordNotRegistered
)
from core import BaseCog

class SetPsn(BaseCog):
    """Cog handling setting and updating user psn id."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.user_builder = UserBuilder()
        self.discord_builder = DiscordBuilder()

    @app_commands.command(
        name="account_set_psn",
        description="Set or update psn id bound to account."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.account_set_psn.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def set_psn(
        self,
        interaction: discord.Interaction,
        psn_name: str
    ):
        """Reset account token."""
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            try:
                # Check if user is registered.
                discord_user = await self.discord_builder.select_discord_user(
                    session, str(interaction.user.id)
                )
                if discord_user is None:
                    raise DiscordNotRegistered(
                        "No account registered for this discord user."
                    )

                if not await self.user_builder.update_user_psn(
                    session,
                    discord_user.user_id,
                    psn_name
                ):
                    raise CoroutineFailed(
                        "Could not update table."
                    )

                logging.info("%s: %s", interaction.user.id, "Token Reset")
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Psn ID Updated.",
                        color=discord.Color.green()
                    ),
                    ephemeral=True
                )

                # Commit
                await session.commit()

            except (
                DiscordNotRegistered
            ) as e:
                logging.warning("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Psn ID update failed.",
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
                        title="Psn ID update failed.",
                        description=e,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

            finally:
                # Close Session
                await session.close()

    @set_psn.error
    async def on_account_token_reset_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.account_set_psn.enabled:
        await client.add_cog(SetPsn(client))

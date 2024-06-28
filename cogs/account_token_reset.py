"""Extension module for AccountTokenReset Cog."""
import logging

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import UserBuilder, DiscordBuilder
from core import (
    CoroutineFailed,
    UsernameIncorrect,
    UnmatchingPasswords,
    DiscordNotRegistered
)
from core import BaseCog
from core.crypto import check_password

class AccountTokenReset(BaseCog):
    """Cog handling token reset with credentials."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.user_builder = UserBuilder()
        self.discord_builder = DiscordBuilder()

    @app_commands.command(
        name="account_token_reset",
        description="Reset account token. To generate new token use `!discord` command in game."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.realm.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def account_token_reset(
        self,
        interaction: discord.Interaction,
        username: str,
        password: str
    ):
        """Reset account token."""
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            try:
                user = await self.user_builder.select_user_by_username(session, username)
                if user is None:
                    raise UsernameIncorrect(
                        'Username is incorrect.'
                    )

                if await check_password(password, user.password) is False:
                    raise UnmatchingPasswords(
                        'Passwords do not match.'
                    )

                discord_id = await self.discord_builder.check_id(session, str(interaction.user.id))
                if discord_id is None:
                    raise DiscordNotRegistered(
                        f'{interaction.user.mention} account is not registered.'
                    )

                if not await self.user_builder.clear_user_token(
                    session,
                    user.id
                ):
                    raise CoroutineFailed(
                        "Could not update table."
                    )
                logging.info("%s: %s", interaction.user.id, "Token Reset")
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Token Reset",
                        description="To generate new token use `!discord` command in game.",
                        color=discord.Color.green()
                    ),
                    ephemeral=True
                )

                # Commit
                await session.commit()

            except (
                UsernameIncorrect,
                UnmatchingPasswords,
                UnmatchingPasswords
            ) as e:
                logging.warning("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Token Reset Failed",
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
                        title="Token Reset Failed",
                        description=e,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

            finally:
                # Close Session
                await session.close()

    @account_token_reset.error
    async def on_account_token_reset_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(AccountTokenReset(client))

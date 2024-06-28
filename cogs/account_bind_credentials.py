"""Extension module for AccountBindCredentials Cog."""
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
    UsernameIncorrect,
    UnmatchingPasswords
)
from core import BaseCog
from core.crypto import check_password

class AccountBindCredentials(BaseCog):
    """Cog handling binding account with credentials."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.user_builder = UserBuilder()
        self.discord_builder = DiscordBuilder()

    @app_commands.command(
        name="account_bind_credentials",
        description="Bind user account by ingame credentials."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.realm.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def account_bind_credentials(
        self,
        interaction: discord.Interaction,
        username: str,
        password: str
    ):
        """Bind user account by using ingame credentials."""
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            try:
                # Get user info.
                user = await self.user_builder.select_user_by_username(
                    session,
                    username
                )
                if user is None:
                    raise UsernameIncorrect(
                        'Username is incorrect.'
                    )

                if await check_password(password, user.password) is False:
                    raise UnmatchingPasswords(
                        'Passwords do not match.'
                    )

                discord_id = await self.discord_builder.check_id(
                    session,
                    str(interaction.user.id)
                )
                if discord_id is not None:
                    # Update User
                    if not await self.discord_builder.bind_user_old(
                        session,
                        user.id,
                        str(interaction.user.id)
                    ):
                        raise CoroutineFailed(
                            "Could not update table."
                        )

                    logging.info("%s: %s", interaction.user.id, "Account Updated")
                    await interaction.response.send_message(
                        embed=discord.Embed(
                            title="Account Updated",
                            color=discord.Color.green()
                        ),
                        ephemeral=True
                    )
                else:
                    # Register User
                    await self.discord_builder.bind_user_new(
                        session,
                        user.id,
                        str(interaction.user.id)
                    )
                    logging.info("%s: %s", interaction.user.id, "Account Registered")
                    await interaction.response.send_message(
                        embed=discord.Embed(
                            title="Account Registered",
                            color=discord.Color.green()
                        ),
                        ephemeral=True
                    )
                # Commit
                await session.commit()

            except (
                UsernameIncorrect,
                UnmatchingPasswords
            ) as e:
                logging.warning("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Binding Failed",
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
                        title="Binding Failed",
                        description=e,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

            except Exception as e:
                logging.error("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Binding Failed",
                        description="Unhandled exception.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

            finally:
                # Close Session
                await session.close()

    @account_bind_credentials.error
    async def on_account_bind_credentials_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(AccountBindCredentials(client))

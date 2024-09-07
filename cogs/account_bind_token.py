"""Extension module for AccountBindToken Cog."""
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
    TokenInvalid
)
from core import BaseCog

async def m_bind_token(
    interaction: discord.Interaction,
    user_builder: UserBuilder,
    discord_builder: DiscordBuilder,
    discord_token: str
):
    """Bind user account by using token."""
    # Create session
    async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
    async with async_session() as session:
        try:
            discord_id = await discord_builder.check_id(session, str(interaction.user.id))

            user_id = await user_builder.select_id_by_token(session, discord_token)
            if user_id is None:
                raise TokenInvalid(
                        "User token is invalid."
                    )

            if discord_id is not None:
                # Update User.
                if not await discord_builder.bind_user_old(
                    session,
                    user_id,
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
                await discord_builder.bind_user_new(
                    session,
                    user_id,
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
            TokenInvalid
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

        finally:
            # Close Session
            await session.close()

class ModalBindToken(
    discord.ui.Modal,
    title='Bind Token'
):
    """Discord Modal view class."""
    def __init__(
        self,
        user_builder: UserBuilder,
        discord_builder: DiscordBuilder,
    ):
        super().__init__()
        self.user_builder = user_builder
        self.discord_builder = discord_builder
    token = discord.ui.TextInput(
        label='Token',
        placeholder='Type in your token...',
    )

    async def on_submit(self, interaction: discord.Interaction):
        await m_bind_token(
            interaction,
            self.user_builder,
            self.discord_builder,
            self.token.value
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        logging.error("%s: %s %s %s", interaction.user.id, type(error), error, error.__traceback__)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Binding Failed",
                color=discord.Color.red()
            ),
            ephemeral=True
        )

class AccountBindToken(BaseCog):
    """Cog handling binding account with token."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.user_builder = UserBuilder()
        self.discord_builder = DiscordBuilder()

    @app_commands.command(
        name="account_bind_token",
        description="Bind user account by using token. Use `!discord` in game to obtain user token. (Alternative to credentials)"
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.account_bind_token.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def account_bind_token(self, interaction: discord.Interaction):
        """Bind user account by using token."""
        await interaction.response.send_modal(
            ModalBindToken(self.user_builder, self.discord_builder)
        )

    @account_bind_token.error
    async def on_account_bind_token_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.account_bind_token.enabled:
        await client.add_cog(AccountBindToken(client))

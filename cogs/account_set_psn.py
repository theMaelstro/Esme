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
    DiscordNotRegistered,
    PsnIDAlreadyRegistered
)
from core import BaseCog

async def m_set_psn(
    interaction: discord.Interaction,
    user_builder: UserBuilder,
    discord_builder: DiscordBuilder,
    psn_name: str
):
    """Update user bound psn id."""
    # Create session
    async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
    async with async_session() as session:
        try:
            # Check if user is registered.
            discord_user = await discord_builder.select_discord_user(
                session, str(interaction.user.id)
            )
            if discord_user is None:
                raise DiscordNotRegistered(
                    "No account registered for this discord user."
                )

            user = await user_builder.select_user_psn(
                session,
                psn_name
            )
            if user:
                print(user)
                print(user.id)
                if not user.id == discord_user.user_id:
                    raise PsnIDAlreadyRegistered(
                        "Psn ID already registered. Please use different Psn ID."
                    )

            if not await user_builder.update_user_psn(
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
            DiscordNotRegistered,
            PsnIDAlreadyRegistered
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

class ModalPsn(
    discord.ui.Modal,
    title='Set PSN'
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
    psn = discord.ui.TextInput(
        label='PSN ID',
        placeholder='Type in your PSN ID...',
    )

    async def on_submit(self, interaction: discord.Interaction):
        await m_set_psn(
            interaction,
            self.user_builder,
            self.discord_builder,
            self.psn.value
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        logging.error("%s: %s %s %s", interaction.user.id, type(error), error, error.__traceback__)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Psn ID update failed.",
                color=discord.Color.red()
            ),
            ephemeral=True
        )

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
        interaction: discord.Interaction
    ):
        """Update user bound psn id."""
        await interaction.response.send_modal(
            ModalPsn(self.user_builder, self.discord_builder)
        )

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

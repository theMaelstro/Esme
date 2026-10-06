"""Extension module for AccountTokenReset Cog."""
import traceback
import logging

import discord
from sqlalchemy.ext.asyncio import async_sessionmaker

from data.connector import CONN
from data import UserBuilder, DiscordBuilder

from settings import CONFIG
from core.exceptions import (
    CoroutineFailed,
    UserNotBound,
    MissingPermissions,
    UnmatchingPasswords,
    UsernameIncorrect,
    TermsRejected
)
from core.crypto import check_password

async def m_token_reset(
        interaction: discord.Interaction,
        user_builder: UserBuilder,
        discord_builder: DiscordBuilder,
        username: str,
        password: str
):
    """Reset account token."""
    try:
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            user = await user_builder.select_user_by_username(session, username)
            if user is None:
                raise UsernameIncorrect(
                    'Username is incorrect.'
                )

            if await check_password(password, user.password) is False:
                raise UnmatchingPasswords(
                    'Passwords do not match.'
                )

            if not await user_builder.clear_user_token(
                session,
                user.id
            ):
                raise CoroutineFailed(
                    "Could not update table."
                )
            logging.info("%s: %s", interaction.user.id, "Token Reset")
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Token Reset Success",
                    description="To generate new token use `!discord` command in game.",
                    color=discord.Color.green()
                ),
                ephemeral=True
            )

            # Commit
            await session.commit()
            await session.close()

    except (
        UnmatchingPasswords,
        UsernameIncorrect
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
                description="Internal Error",
                color=discord.Color.red()
            ),
            ephemeral=True
        )

class ModalTokenReset(
    discord.ui.Modal,
    title='Token Reset'
):
    """Discord Modal view class."""
    def __init__(
        self,
        user_builder: UserBuilder,
        discord_builder: DiscordBuilder
    ):
        super().__init__()
        self.user_builder = user_builder
        self.discord_builder = discord_builder
    username = discord.ui.TextInput(
        label='Username',
        placeholder='Type in your username...',
    )
    password = discord.ui.TextInput(
        label='Game Password (encrypted in the process)',
        placeholder='Type in your game password...',
    )

    async def on_submit(self, interaction: discord.Interaction):
        await m_token_reset(
            interaction,
            self.user_builder,
            self.discord_builder,
            self.username.value,
            self.password.value
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        logging.error("%s: %s %s %s", interaction.user.id, type(error), error, traceback.format_exc())
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Token Reset Failed",
                color=discord.Color.red()
            ),
            ephemeral=True
        )

class TokenReset():
    """Cog handling token reset with credentials."""
    def __init__(self):
        self.user_builder = UserBuilder()
        self.discord_builder = DiscordBuilder()

    async def token_reset(
        self,
        interaction: discord.Interaction
    ):
        """Reset account token."""
        try:
            if not CONFIG.check_permission(
                CONFIG.commands.account_token_reset.permission,
                interaction.user
            ):
                raise MissingPermissions(
                    f"{interaction.user.mention} is missing permissions to use command."
                )
            # Create session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                # Create session
                async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
                async with async_session() as session:
                    # Check if user is registered.
                    discord_user = await self.discord_builder.select_discord_user(
                        session,
                        str(interaction.user.id)
                    )

                    if discord_user is None:
                        raise TermsRejected()

                    meta = await self.discord_builder.select_meta(
                        session,
                        "terms"
                    )

                    if discord_user.terms != meta['sha']:
                        raise TermsRejected()

                    if discord_user.user_id is None:
                        raise UserNotBound(
                            "No account registered for this discord user."
                        )

                    # Commit
                    await session.commit()
                    await session.close()

            await interaction.response.send_modal(
                ModalTokenReset(self.user_builder, self.discord_builder)
            )

        except (
            UserNotBound,
            MissingPermissions
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
            TermsRejected
        ) as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Token Reset Failed",
                    description=e.readable,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        except (
            Exception
        ) as e:
            logging.error("%s: %s %s %s", interaction.user.id, type(e), e, traceback.format_exc())
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Procesing Failed",
                    description="Internal Error.",
                    color=discord.Color.red()
                ),
                view=None
            )

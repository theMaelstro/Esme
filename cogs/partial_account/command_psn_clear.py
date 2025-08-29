"""Extension module for Account Cog."""
import logging

import discord
from sqlalchemy.ext.asyncio import async_sessionmaker

from data.connector import CONN
from data import UserBuilder, DiscordBuilder

from settings import CONFIG
from core.exceptions import (
    CoroutineFailed,
    DiscordNotRegistered,
    MissingPermissions
)

class PsnClear():
    """Cog handling psn reset with credentials."""
    def __init__(self):
        self.user_builder = UserBuilder()
        self.discord_builder = DiscordBuilder()

    async def psn_clear(self, interaction: discord.Interaction):
        """Reset account psn."""
        try:
            if not CONFIG.check_permission(
                CONFIG.commands.account_psn_clear.permission,
                interaction.user
            ):
                raise MissingPermissions(
                    f"{interaction.user.mention} is missing permissions to use command."
                )

            # Create session
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

                if not await self.user_builder.clear_user_psn(
                    session,
                    discord_user.user_id
                ):
                    raise CoroutineFailed(
                        "Could not update table."
                    )
                logging.info("%s: %s", interaction.user.id, "Psn Clear")
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Psn Clear Success",
                        color=discord.Color.green()
                    ),
                    ephemeral=True
                )

                # Commit
                await session.commit()
                await session.close()

        except (
            DiscordNotRegistered,
            MissingPermissions
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Psn Clear Failed",
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
                    title="Psn Clear Failed",
                    description="Internal Error.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

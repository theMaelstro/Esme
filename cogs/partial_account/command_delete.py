"""Extension module for AccountCard Cog."""
import re
import logging

import discord
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import (
    DiscordBuilder
)
from core.exceptions import (
    CoroutineFailed,
    CharacterNotSet,
    UserNotBound,
    MissingPermissions
)

class DeleteData():
    """
    Cog handling account deletion.
    """
    def __init__(self):
        self.discord_builder = DiscordBuilder()

    async def delete(self, interaction: discord.Interaction, member: discord.Member):
        """Delete account."""
        try:
            if member is None:
                member = interaction.user
            elevated = CONFIG.check_permission(
                CONFIG.commands.account_card.admin_permission,
                interaction.user
            )
            permitted = CONFIG.check_permission(
                CONFIG.commands.account_change_password.permission,
                interaction.user
            )
            owner = interaction.user.id == member.id if member else False

            if not (elevated or (permitted and owner)):
                raise MissingPermissions(
                    f"{interaction.user.mention} is missing permissions to use command."
                )

            # Create session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                # Check if user is registered.
                discord_user = await self.discord_builder.select_discord_user(
                    session, str(interaction.user.id) if not member else str(member.id)
                )

                if discord_user is None:
                    raise UserNotBound(
                        "No account registered for this discord user."
                    )

                response = await self.discord_builder.delete_user(
                    session, discord_user.id
                )

                # Close Session
                await session.commit()
                await session.close()

                if not response:
                    raise CoroutineFailed(
                        "Internal Error."
                    )

                logging.info("User erased: %s", response)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Data Deletion Completed",
                        color=discord.Color.green()
                    ),
                    ephemeral=True
                )

        except (
            CoroutineFailed,
            CharacterNotSet,
            UserNotBound,
            MissingPermissions
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Data Deletion Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

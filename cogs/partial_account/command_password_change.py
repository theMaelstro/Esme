"""Extension module for PasswordChange Cog."""
import traceback
import logging

import discord
from sqlalchemy.ext.asyncio import async_sessionmaker
from data.connector import CONN
from data import (
    DiscordBuilder,
    UserBuilder
)

from settings import CONFIG
from core.exceptions import (
    CoroutineFailed,
    DiscordNotRegistered,
    IncorrectPasswordHash,
    MissingPermissions
)

async def m_change_password(
    interaction: discord.Interaction,
    member: discord.Member,
    user_builder: UserBuilder,
    discord_builder: DiscordBuilder,
    password_hash: str
):
    """Change user password."""
    try:
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            # Check if user is registered.
            discord_user = await discord_builder.select_discord_user(
                session, str(interaction.user.id) if not member else str(member.id)
            )

            if discord_user is None:
                raise DiscordNotRegistered(
                    "No account registered for this discord user."
                )

            split_hash = password_hash.split("$")
            if (
                len(split_hash) < 4
                or split_hash[1] != "2a"
                or int(split_hash[2]) < 10
                or len(split_hash[3]) < 53
            ):

                raise IncorrectPasswordHash()

            # Update Password.
            if not await user_builder.update_password(
                session,
                discord_user.user_id,
                password_hash
            ):
                raise CoroutineFailed(
                    "Could not update table."
                )

            logging.info("%s: %s", interaction.user.id, "Password Updated")
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Password Updated",
                    color=discord.Color.green()
                ),
                ephemeral=True
            )

            # Commit
            await session.commit()
            await session.close()

    #except (
    #    TokenInvalid
    #) as e:
    #    logging.warning("%s: %s", interaction.user.id, e)
    #    await interaction.response.send_message(
    #        embed=discord.Embed(
    #            title="Binding Failed",
    #            description=e,
    #            color=discord.Color.red()
    #        ),
    #        ephemeral=True
    #    )

    except (
        CoroutineFailed
    ) as e:
        logging.error("%s: %s", interaction.user.id, e)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Password Change Failed",
                description="Internal Error.",
                color=discord.Color.red()
            ),
            ephemeral=True
        )

class ModalChangePassword(
    discord.ui.Modal,
    title='Change Password'
):
    """Discord Modal view class."""
    def __init__(
        self,
        user_builder: UserBuilder,
        discord_builder: DiscordBuilder,
        member: discord.Member
    ):
        super().__init__()
        self.user_builder = user_builder
        self.discord_builder = discord_builder
        self.member = member
    password_hash = discord.ui.TextInput(
        label='Hash',
        placeholder='Paste password hash...',
    )

    async def on_submit(self, interaction: discord.Interaction):
        await m_change_password(
            interaction,
            self.member,
            self.user_builder,
            self.discord_builder,
            self.password_hash.value
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        logging.error("%s: %s %s %s", interaction.user.id, type(error), error, traceback.format_exc())
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Password Change Failed",
                color=discord.Color.red()
            ),
            ephemeral=True
        )

class PasswordChange():
    """Invoke Modal for password change."""
    def __init__(self):
        self.user_builder = UserBuilder()
        self.discord_builder = DiscordBuilder()

    async def change_password(self, interaction: discord.Interaction, member: discord.Member):
        """Change user password."""
        try:
            logging.info("%s: %s", "Member: ", member)
            if member == None:
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
            await interaction.response.send_modal(
                ModalChangePassword(self.user_builder, self.discord_builder, member)
            )

        except (
            MissingPermissions
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Password Change Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

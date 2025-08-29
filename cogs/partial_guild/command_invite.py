"""Extension module for GuildMembers Cog."""
import logging

import discord
from sqlalchemy.ext.asyncio import async_sessionmaker

from data.connector import CONN
from data import (
    CharactersBuilder,
    DiscordBuilder,
    GuildBuilder
)

from settings import CONFIG
from core.exceptions import (
    CharacterAlreadyInGuild,
    CharacterNotSet,
    CharacterPendingInvite,
    DiscordNotRegistered,
    GuildFull,
    MissingPermissions,
    UsersAreEqual
)
from core import max_members

class GuildInvite():
    """Holder for members list command."""
    def __init__(self):
        self.character_builder = CharactersBuilder()
        self.discord_builder = DiscordBuilder()
        self.guild_builder = GuildBuilder()

    async def guild_invite(self, interaction: discord.Interaction, member: discord.Member):
        """Show all guilds."""
        try:
            if not CONFIG.check_permission(
                CONFIG.commands.guild_invite.permission,
                interaction.user
            ):
                raise MissingPermissions(
                    f"{interaction.user.mention} is missing permissions to use command."
                )

            if interaction.user.id == member.id:
                raise UsersAreEqual(
                    "You can't invite yourself."
                )

            # Start session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                # Check if sender is registered.
                discord_sender = await self.discord_builder.select_discord_user(
                    session, str(interaction.user.id)
                )
                if discord_sender is None:
                    raise DiscordNotRegistered(
                        "No account registered for this discord user."
                )

                # Check if recipient is registered.
                discord_recipient = await self.discord_builder.select_discord_user(
                    session, str(member.id)
                )
                if discord_recipient is None:
                    raise DiscordNotRegistered(
                        "Recipient discord user is not registered."
                    )

                if not discord_sender.character_id:
                    raise CharacterNotSet(
                        "Sender has not selected character."
                    )

                if not discord_recipient.character_id:
                    raise CharacterNotSet(
                        "Recipient has not selected character."
                    )

                # Get sender character.
                sender_character = await self.guild_builder.select_guild_character_details_by_character_id(
                    session,
                    discord_sender.character_id
                )

                discord_ids = await self.guild_builder.select_recruiter_discord_ids(
                    session,
                    sender_character.guild_id
                )
                if str(interaction.user.id) not in discord_ids:
                    raise MissingPermissions(
                        "You are not elevated guild member."
                    )

                guild = await self.guild_builder.select_recruiting_guild_by_id(
                    session,
                    sender_character.guild_id
                )

                if guild.members >= max_members(guild.guild_rp):
                    raise GuildFull(
                        "Guild is full and cannot accept new members."
                    )

                # Get recipient character.
                recipient_character = await self.character_builder.select_character_details_by_character_id(
                    session,
                    discord_recipient.character_id
                )

                if recipient_character.guild_id:
                    raise CharacterAlreadyInGuild(
                        "Character aleady in guild."
                    )

                application_check = await self.guild_builder.check_guild_application(
                    session,
                    discord_recipient.character_id,
                    sender_character.guild_id
                )

                if application_check:
                    raise CharacterPendingInvite(
                        "Character is already pending invite from guild."
                    )

                await self.guild_builder.insert_guild_application(
                    session,
                    sender_character.guild_id,
                    discord_recipient.character_id,
                    discord_sender.character_id,
                    application_type="invited"
                )

                # Send in-game mail.
                sender_id = discord_sender.character_id
                recipient_id = discord_recipient.character_id
                subject = "Invitation!"
                body = (
                    "You have been invited to join\n"
                    f"「{sender_character.guild_name}」\n"
                    "Do you want to accept?"
                )
                await self.character_builder.insert_message(
                    session,
                    sender_id,
                    recipient_id,
                    subject=subject,
                    body=body,
                    is_guild_invite=True
                )

                # Close Session
                await session.commit()
                await session.close()

                logging.info("%s: %s", interaction.user.id, "Invitation Sent")
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Invitation Sent",
                        color=discord.Color.green()
                    ),
                    ephemeral=True
                )

        except (
            CharacterAlreadyInGuild,
            CharacterNotSet,
            CharacterPendingInvite,
            DiscordNotRegistered,
            GuildFull,
            MissingPermissions,
            UsersAreEqual
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Invitation Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        except (
            Exception
        ) as e:
            logging.error("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Invitation Failed",
                    description="Internal Error",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

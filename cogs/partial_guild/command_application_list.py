"""Guild application list command."""
import re
import traceback
import logging

import discord
from sqlalchemy.ext.asyncio import async_sessionmaker

from data.connector import CONN
from data import (
    DiscordBuilder,
    GuildBuilder
)

from core.exceptions import (
    CoroutineFailed,
    DiscordNotRegistered,
    GuildFull,
    InvalidArgument,
    MissingPermissions,
    CharacterNotInGuild,
    CharacterNotSet,
    MissingGuildApplications
)
from core import max_members

def get_app_type_emoji(application_type: bool):
    if application_type:
        return "📥"
    return "📤"

def get_app_type(
        application_type: str
) -> bool:
    if application_type == "applied":
        return True
    return False

def get_option_data(options_list, match):
    for element in options_list:
        if str(element.value) == str(match):
            return {
                "value": element.value,
                "label": element.label,
                "type": element.description
            }
    return None

class DynamicApplicationView(discord.ui.View):
    def __init__(
            self,
            option_data: dict,
            user_is_leader: bool,
            *,
            timeout = 180,
        ):
        super().__init__(timeout=timeout)
        self.discord_builder = DiscordBuilder()
        self.guild_builder = GuildBuilder()
        self.application_id = option_data["value"]
        self.application_character = option_data["label"]
        self.application_type = option_data["type"]
        self.user_is_leader=user_is_leader
        self.update_buttons()

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, disabled=True)
    async def app_accept(self, interaction: discord.Interaction, button: discord.Button):
        try:
            # Start session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                guild_application = await self.guild_builder.select_guild_application_by_id(
                    session,
                    self.application_id
                )
                if not guild_application:
                    raise(
                        CoroutineFailed(
                            "Applictaion does not exist."
                        )
                    )

                guild = await self.guild_builder.select_recruiting_guild_by_id(
                    session,
                    guild_application.guild_id
                )
                if guild.members >= max_members(guild.guild_rp):
                    raise GuildFull(
                        "Guild is full and cannot accept new members."
                    )

                await self.guild_builder.insert_guild_member(
                    session,
                    guild_application.guild_id,
                    guild_application.character_id
                )
                await self.guild_builder.delete_guild_applications(
                    session,
                    guild_application.character_id
                )

                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="Application Accepted",
                        description=f"{self.application_character} application accepted.",
                        color=discord.Color.green()
                    ),
                    view=None
                )

                # Close Session
                await session.commit()
                await session.close()
        except (
            GuildFull
        ) as e:
            logging.info("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Application Process Failed",
                    description="Guild is full and cannot accept more members.",
                    color=discord.Color.blue()
                ),
                ephemeral=True
            )
        except (
            CoroutineFailed
        ) as e:
            logging.error("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Application Process Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def app_reject(self, interaction: discord.Interaction, button: discord.Button):
        try:
            # Start session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                await self.guild_builder.delete_guild_application(
                    session,
                    self.application_id
                )

                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="Application Rejected",
                        description=f"{self.application_character} application cancelled.",
                        color=discord.Color.red()
                    ),
                    view=None
                )

                # Close Session
                await session.commit()
                await session.close()

        except (
            CoroutineFailed
        ) as e:
            logging.error("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Application Process Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray)
    async def app_cancel(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Cancelled",
                description="Guild Application resolution cancelled.",
                color=discord.Color.green()
            ),
            view=None
        )

    def update_buttons(self):
        if self.application_type == "applied":
            self.children[0].disabled = not self.user_is_leader
        else:
            self.children[0].disabled = self.user_is_leader

class DynamicSelect(discord.ui.Select):
    def __init__(
            self,
            options: list,
            user_is_leader: bool
        ) -> None:
        super().__init__(
            placeholder="Select an option",
            max_values=1,
            min_values=1,
            options=options
        )
        self.user_is_leader = user_is_leader

    async def callback(self, interaction: discord.Interaction):
        data = get_option_data(self.options, self.values[0])
        await interaction.response.edit_message(
            embed=discord.Embed(
                title=data["label"],
                description="Please resolve application.",
                color=discord.Color.blue()
            ),
            view=DynamicApplicationView(data, self.user_is_leader)
        )

class DynamicSelectView(discord.ui.View):
    def __init__(
            self,
            options: list,
            user_is_leader: bool,
            *,
            timeout = 180
        ):
        super().__init__(timeout=timeout)
        self.add_item(DynamicSelect(options, user_is_leader))

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray)
    async def app_cancel(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Cancelled",
                description="Guild Application resolution cancelled.",
                color=discord.Color.green()
            ),
            view=None
        )

class ApplicationList():
    """Holder for application list command."""
    def __init__(self):
        self.discord_builder = DiscordBuilder()
        self.guild_builder = GuildBuilder()
        self.user_is_leader: bool = None

    async def guild_application(
        self,
        interaction: discord.Interaction,
    ):
        """Manage guild applications."""
        try:
            # Start session
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

                if discord_user.character_id is None:
                    raise CharacterNotSet(
                        "No character selected. Please use `/account character select` command."
                    )

                guild_character = await self.guild_builder.select_guild_character_by_character_id(
                    session, discord_user.character_id
                )

                if guild_character:
                    discord_ids = await self.guild_builder.select_recruiter_discord_ids(
                        session,
                        guild_character.guild_id
                    )

                    if str(interaction.user.id) not in discord_ids:
                        raise MissingPermissions(
                            "You are not elevated guild member."
                        )

                    self.user_is_leader = True
                    guild_applications = await self.guild_builder.select_guild_applications_detail_by_guild_id(
                        session,
                        guild_character.guild_id
                    )

                    if guild_applications is None or len(guild_applications) <= 0:
                        raise MissingGuildApplications(
                            "No Guild Applications found."
                        )
                
                else:
                    self.user_is_leader = False
                    guild_applications = await self.guild_builder.select_guild_applications_detail_by_character_id(
                        session,
                        discord_user.character_id
                    )

                    if guild_applications is None or len(guild_applications) <= 0:
                        raise MissingGuildApplications(
                            "No Guild Applications found."
                        )

                # Close Session
                await session.commit()
                await session.close()

            options = []
            if isinstance(guild_applications, list):
                if self.user_is_leader:
                    for application in guild_applications:
                        options.append(
                            discord.SelectOption(
                                label=f"{re.escape(application.character_name)}",
                                value=application.id,
                                emoji=get_app_type_emoji(get_app_type(application.type)),
                                description=f"{application.type}"
                            )
                        )
                else:
                    for application in guild_applications:
                        options.append(
                            discord.SelectOption(
                                label=f"{re.escape(application.guild_name)}",
                                value=application.id,
                                emoji=get_app_type_emoji(not get_app_type(application.type)),
                                description=f"{application.type}"
                            )
                        )

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Select Guild Application",
                    color=discord.Color.blue()
                ),
                view=DynamicSelectView(options, self.user_is_leader),
                ephemeral=True
            )

        except (
            MissingGuildApplications
        ) as e:
            logging.info("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Application List",
                    description="No applications pending.",
                    color=discord.Color.blue()
                ),
                ephemeral=True
            )
        except (
            DiscordNotRegistered,
            InvalidArgument,
            MissingPermissions,
            CharacterNotInGuild,
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Application Process Failed",
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
                    title="Application Process Failed",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
        except (
            Exception
        ) as e:
            logging.error("%s: %s", interaction.user.id, traceback.format_exc())
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Application Process Failed",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

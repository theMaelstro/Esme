"""Guild application list command."""
import re
import traceback
import logging

import discord
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import (
    DiscordBuilder,
    GuildBuilder
)

from core.exceptions import (
    CoroutineFailed,
    DiscordNotRegistered,
    InvalidArgument,
    MissingPermissions,
    CharacterNotInGuild,
    MissingGuildApplications
)
def get_app_type_emoji(type):
    return "📥" if type == "applied" else "📤"

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
            *,
            timeout = 180,
        ):
        super().__init__(timeout=timeout)
        self.discord_builder = DiscordBuilder()
        self.guild_builder = GuildBuilder()
        self.application_id = option_data["value"]
        self.application_character = option_data["label"]
        self.application_type = option_data["type"]
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
                await self.guild_builder.insert_guild_member(
                    session,
                    guild_application.guild_id,
                    guild_application.character_id
                )
                await self.guild_builder.delete_guild_application(
                    session,
                    self.application_id
                )

                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="Application Accepted",
                        description=f"{self.application_character} has been accepted into the guild.",
                        color=discord.Color.green()
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
                        description=f"{self.application_character} has been rejected from joining the guild.",
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
            self.children[0].disabled = False
        else:
            self.children[0].disabled = True

class DynamicSelect(discord.ui.Select):
    def __init__(self, options: list) -> None:
        super().__init__(
            placeholder="Select an option",
            max_values=1,
            min_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        data = get_option_data(self.options, self.values[0])
        await interaction.response.edit_message(
            embed=discord.Embed(
                title=data["label"],
                description="Please resolve application.",
                color=discord.Color.blue()
            ),
            view=DynamicApplicationView(data)
        )

class DynamicSelectView(discord.ui.View):
    def __init__(self, options: list, *, timeout = 180):
        super().__init__(timeout=timeout)
        self.add_item(DynamicSelect(options))

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

                guild_character = await self.guild_builder.select_guild_character_by_character_id(
                    session, discord_user.character_id
                )

                if guild_character is None:
                    raise CharacterNotInGuild(
                        "Character is not a Guild member."
                    )

                discord_ids = await self.guild_builder.select_recruiter_discord_ids(
                    session,
                    guild_character.guild_id
                )
                print("sqtest: command: ", discord_ids, guild_character, guild_character.guild_id)
                if str(interaction.user.id) not in discord_ids:
                    raise MissingPermissions(
                        "You are not elevated guild member."
                    )

                guild_applications = await self.guild_builder.select_guild_applications_detail_by_guild_id(
                    session, guild_character.guild_id
                )

                if guild_applications is None:
                    raise MissingGuildApplications(
                        "No Guild Applications found."
                    )

                # Close Session
                await session.commit()
                await session.close()

            options = []
            if isinstance(guild_applications, list):
                for application in guild_applications:
                    options.append(
                        discord.SelectOption(
                            label=f"{re.escape(application.initiate_name)}",
                            value=application.id,
                            emoji=get_app_type_emoji(application.type),
                            description=f"{application.type}"
                        )
                    )

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Select Guild Application",
                    color=discord.Color.blue()
                ),
                view=DynamicSelectView(options),
                ephemeral=True
            )

        except (
            DiscordNotRegistered,
            InvalidArgument,
            MissingPermissions,
            CharacterNotInGuild,
            MissingGuildApplications

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
                    description=e,
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
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

"""Extension module for example Ping Cog with response interaction."""
import logging
from typing import Callable

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
import discord
from discord.ext import commands
from discord import app_commands

from settings import CONFIG
from core import BaseCog
from core.exceptions import (
    CoroutineFailed,
    DiscordNotRegistered,
    MissingPermissions
)

from data.connector import CONN
from data import (
    DiscordBuilder,
    UserBuilder
)

def get_option_data(options_list):
    return {
        element.value: {
            "label": element.label,
            "type": element.description
        } for element in options_list
    }

class DynamicSelect(discord.ui.Select):
    def __init__(
            self,
            options: list,
            my_bin: str,
            respone: Callable
        ) -> None:
        super().__init__(
            placeholder="Select an option",
            max_values=len(options),
            min_values=1,
            options=options
        )
        self.my_bin=my_bin
        self.response = respone

    async def callback(self, interaction: discord.Interaction):
        data = get_option_data(self.options)
        values = self.values

        rows = ""
        for row in values:
            rows=rows+f"`{data[int(row)]["label"]}`\n"
            if int(row) > 1:
                self.my_bin =  self.my_bin[:-int(row)] + '1' + self.my_bin[-int(row)+1:]
            else:
                self.my_bin =  self.my_bin[:-int(row)] + '1'

        try:
            await self.response(int(self.my_bin, base=2))
            await interaction.response.edit_message(
            embed=discord.Embed(
                title="Active Courses",
                description=rows,
                color=discord.Color.blue()
            ),
            view=None
        )
        except (
            CoroutineFailed
        ) as e:
            logging.error("%s: %s", interaction.user.id, e)
            await interaction.response.edit_message(
                view=self.view,
                embed=discord.Embed(
                    title="Course Update Failed",
                    description=e,
                    color=discord.Color.red()
                )
            )

class DynamicSelectView(discord.ui.View):
    def __init__(
            self,
            options: list,
            my_bin: str,
            session: async_sessionmaker[AsyncSession],
            query_call: Callable,
            *,
            timeout = 180
    ):
        super().__init__(timeout=timeout)
        self.add_item(DynamicSelect(options, my_bin, self.response))
        self.session = session
        self.query_call = query_call

    async def response(self, query_value):
        """Response callback function for selection menu."""
        if self.query_call:
            await self.query_call(query_value)
        await self._close_session()
        self._disable_all()

    async def _close_session(self):
        if self.session:
            # Close Session
            logging.info("%s", "Poogie Session Closed.")
            await self.session.commit()
            await self.session.close()

    def _disable_all(self) -> None:
        for item in self.children:
            if isinstance(item, (discord.ui.Button, DynamicSelect)):
                self.remove_item(item)

    async def on_timeout(self) -> None:
        # disable all components
        await self._close_session()
        self._disable_all()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray)
    async def app_cancel(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Cancelled",
                description="Course choice cancelled.",
                color=discord.Color.green()
            ),
            view=None
        )

class Course(BaseCog):
    """Cog example with basic interaction response."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.user_builder = UserBuilder()
        self.discord_builder = DiscordBuilder()

    @app_commands.command(
        name="course",
        description="Subscribe to selection of available courses."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.account_course.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def course(self, interaction: discord.Interaction):
        """Handle course calculation and update."""
        try:
            if not CONFIG.check_permission(
                CONFIG.commands.account_course.permission,
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

                user_rights = await self.user_builder.select_user_rights(session, discord_user.user_id)
                if not user_rights:
                    raise CoroutineFailed(
                        "Invalid rights."
                    )

                my_int = user_rights.rights
                my_bin = f'{my_int:029b}'[-29:]

            options = []
            if isinstance(CONFIG.features.courses, list):
                for course in CONFIG.features.courses:
                    if course.enabled is True:
                        options.append(
                            discord.SelectOption(
                                label=course.name,
                                value=course.mask,
                                description=course.description,
                                default=int(my_bin[-course.mask])
                            )
                        )
                        if course.mask > 1:
                            my_bin = my_bin[:-course.mask] + '0' + my_bin[-course.mask+1:]
                        else:
                            my_bin = my_bin[:-course.mask] + '0'

            async def callback(rights: int):
                if not await self.user_builder.update_user_rights(
                    session,
                    discord_user.user_id,
                    rights
                ):
                    raise CoroutineFailed(
                        "Could not update table."
                    )

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Pick Courses",
                    color=discord.Color.blue()
                ),
                view=DynamicSelectView(options, my_bin, session=session, query_call=callback),
                ephemeral=True
            )

        except (
            MissingPermissions
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Course Select Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @course.error
    async def on_course_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.ping.enabled:
        await client.add_cog(Course(client))

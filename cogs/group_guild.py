import discord
from discord.ext import commands
from discord import app_commands

from settings import CONFIG
from core import BaseCog

from .partial_guild import (
    ApplicationList,
    ApplicationResolve,
    MembersList
)

class GuildCog(BaseCog):
    """Cog handling guild applications."""
    def __init__(self, client: commands.Bot):
        self.client = client

    group_guild = app_commands.Group(
        name="guild",
        description="..."
    )
    group_applications = app_commands.Group(
        name="application",
        parent = group_guild,
        description="..."
    )
    group_members = app_commands.Group(
        name="members",
        parent = group_guild,
        description="..."
    )

    @group_applications.command(name="list")
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.guild_application.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def guild_application_list(self, interaction: discord.Interaction) -> None:
        """Lists 25 oldest applications in your guild to resolve them individually."""
        partial_applications = ApplicationList()
        await partial_applications.guild_application(interaction)

    @group_applications.command(name="accept")
    @app_commands.rename(application_id='id')
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.guild_application.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def guild_application_accept(
        self,
        interaction: discord.Interaction,
        application_id: app_commands.Range[int, 0],
    ) -> None:
        """Accept guild application by ID."""
        partial_applications = ApplicationResolve()
        await partial_applications.guild_application(interaction, application_id, True)

    @group_applications.command(name="reject")
    @app_commands.rename(application_id='id')
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.guild_application.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def guild_application_reject(
        self,
        interaction: discord.Interaction,
        application_id: app_commands.Range[int, 0],
    ) -> None:
        """Reject guild application by ID."""
        partial_applications = ApplicationResolve()
        await partial_applications.guild_application(interaction, application_id, False)

    @group_members.command(name="list")
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.guild_members.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def guild_members_list(self, interaction: discord.Interaction) -> None:
        """Lists members of your guild."""
        partial_members = MembersList()
        await partial_members.guild_members(interaction)

    @guild_application_list.error
    @guild_application_accept.error
    @guild_application_reject.error
    @guild_members_list.error
    async def on_guild_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.guild_set_leader.enabled:
        await client.add_cog(GuildCog(client))

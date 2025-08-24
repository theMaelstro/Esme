from typing import Optional, List

import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

from settings import CONFIG
from core import BaseCog

from .partial_guild import (
    ApplicationList,
    ApplicationResolve,
    GuildApply,
    GuildInvite,
    MembersList,
    MemberExpel
)

class GuildCog(BaseCog):
    """Cog handling guild applications."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.app_guild_invite = app_commands.ContextMenu(
            name='Guild Invite',
            callback = self.guild_invite_app,
        )
        self.client.tree.add_command(self.app_guild_invite)

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

    async def guild_member_expel_name_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[Choice[str]]:
        """Member expel member name autocomplete callback."""
        partial_members_expel = MemberExpel()
        return await partial_members_expel.guild_expel_autocomplete(interaction, current)

    @group_members.command(name="expel")
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.guild_members.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    @app_commands.autocomplete(character_name=guild_member_expel_name_autocomplete)
    async def guild_members_expel(
        self,
        interaction: discord.Interaction,
        character_name: str
    ) -> None:
        """Expel member from guild."""
        partial_members_expel = MemberExpel()
        await partial_members_expel.guild_expel(interaction, character_name)

    async def guild_apply_name_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[Choice[str]]:
        """Guild apply guild name autocomplete callback."""
        partial_apply = GuildApply()
        return await partial_apply.guild_apply_autocomplete(interaction, current)

    @group_guild.command(name="apply")
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.guild_members.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    @app_commands.autocomplete(guild_name=guild_apply_name_autocomplete)
    async def guild_apply(
        self,
        interaction: discord.Interaction,
        guild_name: str
    ) -> None:
        """Invite registered discord user to guild."""
        partial_apply = GuildApply()
        await partial_apply.guild_apply(interaction, guild_name)

    @group_guild.command(name="invite")
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.guild_members.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def guild_invite(self, interaction: discord.Interaction, member: discord.Member) -> None:
        """Invite registered discord user to guild."""
        partial_invite = GuildInvite()
        await partial_invite.guild_invite(interaction, member)

    # Guild Invite Application Command
    async def guild_invite_app(
            self,
            interaction: discord.Interaction,
            member: discord.Member
    ):
        """Display your character information card."""
        partial_invite = GuildInvite()
        await partial_invite.guild_invite(interaction, member)

    @guild_application_list.error
    @guild_application_accept.error
    @guild_application_reject.error
    @guild_members_list.error
    @guild_invite.error
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

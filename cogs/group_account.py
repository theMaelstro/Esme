import discord
from discord.ext import commands
from discord import app_commands

from settings import CONFIG
from core import BaseCog

from .partial_account import (
    BindCredentials,
    BindToken,
    Card,
    PsnSet,
    TokenReset
)

class AccountCog(BaseCog):
    """Cog handling guild applications."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.app_card = app_commands.ContextMenu(
            name='Player Card (Admin)',
            callback = self.card_admin,
        )
        self.client.tree.add_command(self.app_card)

    group_account = app_commands.Group(
        name="account",
        description="..."
    )
    group_bind = app_commands.Group(
        name="bind",
        parent = group_account,
        description="..."
    )
    group_psn = app_commands.Group(
        name="psn",
        parent = group_account,
        description="..."
    )
    group_token = app_commands.Group(
        name="token",
        parent = group_account,
        description="..."
    )

    @group_account.command(name="card")
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.account_card.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def account_card(self, interaction: discord.Interaction) -> None:
        """Display your character information card."""
        partial_card = Card()
        await partial_card.card(interaction, None)

    # Card Application Command
    async def card_admin(
            self,
            interaction: discord.Interaction,
            member: discord.Member
    ):
        """Display your character information card."""
        if interaction.user.id in CONFIG.discord.admin_user_ids:
            partial_card = Card()
            await partial_card.card(interaction, member)
        else:
            await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Failed",
                        description="You are not allowed to use this command.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

    @group_psn.command(name="set")
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.account_set_psn.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def account_psn_set(self, interaction: discord.Interaction) -> None:
        """Bind PSN ID to your game user account."""
        partial_psn_set = PsnSet()
        await partial_psn_set.psn_set(interaction)

    @group_token.command(name="reset")
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.account_token_reset.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def account_token_reset(self, interaction: discord.Interaction) -> None:
        """Reset your game user account token."""
        partial_token_reset = TokenReset()
        await partial_token_reset.token_reset(interaction)

    @group_bind.command(name="credentials")
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.account_bind_credentials.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def account_bind_credentials(self, interaction: discord.Interaction) -> None:
        """Lists members of your guild."""
        partial_bind_credentials = BindCredentials()
        await partial_bind_credentials.bind_credentials(interaction)

    @group_bind.command(name="token")
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.account_bind_token.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def account_bind_token(self, interaction: discord.Interaction) -> None:
        """Lists members of your guild."""
        partial_bind_token = BindToken()
        await partial_bind_token.bind_token(interaction)

    @account_card.error
    @account_psn_set.error
    @account_token_reset.error
    @account_bind_credentials.error
    @account_bind_token.error
    async def on_account_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.guild_set_leader.enabled:
        await client.add_cog(AccountCog(client))

import time

import discord
from discord.ext import commands
from discord import app_commands

from settings import CONFIG
from data import UserBuilder, DiscordBuilder

class AccountBindToken(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.user_builder = UserBuilder()
        self.discord_builder = DiscordBuilder()

    @app_commands.command(
        name="account_bind_token",
        description="Bind user account by using token. Use `!discord` in game to obtain user token."
    )
    @app_commands.checks.cooldown(
    1,
    CONFIG.commands.realm.cooldown,
    key=lambda i: (i.guild_id, i.user.id)
    )
    async def account_bind_token(self, interaction: discord.Interaction, discord_token: str):
        """Bind user account by using token."""
        discord_id = await self.discord_builder.check_id(str(interaction.user.id))
        print("TEST", discord_id)
        if discord_id is not None:
            user_id = await self.user_builder.select_id_by_token(discord_token)
            if user_id:
                await self.discord_builder.bind_user_old(user_id, str(interaction.user.id))
                await interaction.response.send_message(
                    f"Account updated.\nUser ID: *{user_id}*",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "Please provide correct user token",
                    ephemeral=True
                )
        else:
            user_id = await self.user_builder.select_id_by_token(discord_token)
            if user_id:
                await self.discord_builder.bind_user_new(user_id, str(interaction.user.id))
                await interaction.response.send_message(
                    f"Account bound.\nUser ID: *{user_id}*",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "Please provide correct user token",
                    ephemeral=True
                )

    @account_bind_token.error
    async def on_account_bind_token_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        if isinstance(error, app_commands.CommandOnCooldown):
            remaining_time = round(error.retry_after)
            await interaction.response.send_message(
                f"You are on cooldown. Please try again <t:{round(time.time())+remaining_time}:R>",
                ephemeral=True
            )

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(AccountBindToken(client))

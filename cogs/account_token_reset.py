import time

import discord
from discord.ext import commands
from discord import app_commands
import bcrypt

from settings import CONFIG
from data import UserBuilder, DiscordBuilder
from core import UsernameIncorrect, UnmatchingPasswords, DiscordNotRegistered

class AccountTokenReset(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.user_builder = UserBuilder()
        self.discord_builder = DiscordBuilder()

    async def check_password(self, password, stored_hash):
        """Check if password matches stored hash."""
        stored_hash = stored_hash.encode('utf-8')
        #Load hashed from the db and check the provided password
        try:
            if bcrypt.hashpw(
                password.encode('utf-8'),
                bytes(stored_hash)
            ) == bytes(stored_hash):
                return True
        except Exception as e:
            print("CRYPT ERROR", e)
        return False

    @app_commands.command(
        name="account_token_reset",
        description="Reset account token. To generate new token use `!discord` command in game."
    )
    @app_commands.checks.cooldown(
    1,
    CONFIG.commands.realm.cooldown,
    key=lambda i: (i.guild_id, i.user.id)
    )
    async def account_token_reset(
        self,
        interaction: discord.Interaction,
        username: str,
        password: str
    ):
        """Reset account token."""
        try:
            user = await self.user_builder.select_user_by_username(username)
            if user is None:
                raise UsernameIncorrect(
                    'Username is incorrect.'
                )

            if await self.check_password(password, user.password) is False:
                raise UnmatchingPasswords(
                    'Passwords do not match.'
                )

            discord_id = await self.discord_builder.check_id(str(interaction.user.id))
            print("TEST", discord_id)
            if discord_id is not None:
                await self.user_builder.clear_user_token(user.id)
                await interaction.response.send_message(
                    "Token cleared. To generate new token use `!discord` command in game.",
                    ephemeral=True
                )
            else:
                raise DiscordNotRegistered(
                    f'{interaction.user.mention} account is not registered.'
                )

        except (
            UsernameIncorrect,
            UnmatchingPasswords,
            UnmatchingPasswords
        ) as e:
            print("FAILED", e)
            await interaction.response.send_message(
                f"Failed: {e}",
                ephemeral=True
            )

    @account_token_reset.error
    async def on_account_token_reset_error(
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
    await client.add_cog(AccountTokenReset(client))

import time
import logging

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker
import bcrypt

from settings import CONFIG
from data.connector import CONN
from data import UserBuilder, DiscordBuilder
from core import UsernameIncorrect, UnmatchingPasswords

class AccountBindCredentials(commands.Cog):
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
            logging.warning("BCRYPT: %s", e)
        return False

    @app_commands.command(
        name="account_bind_credentials",
        description="Bind user account by ingame credentials."
    )
    @app_commands.checks.cooldown(
    1,
    CONFIG.commands.realm.cooldown,
    key=lambda i: (i.guild_id, i.user.id)
    )
    async def account_bind_credentials(
        self,
        interaction: discord.Interaction,
        username: str,
        password: str
    ):
        """Bind user account by using ingame credentials."""
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            try:
                user = await self.user_builder.select_user_by_username(session, username)
                if user is None:
                    raise UsernameIncorrect(
                        'Username is incorrect.'
                    )

                if await self.check_password(password, user.password) is False:
                    raise UnmatchingPasswords(
                        'Passwords do not match.'
                    )

                discord_id = await self.discord_builder.check_id(session, str(interaction.user.id))
                if discord_id is not None:
                    await self.discord_builder.bind_user_old(session, user.id, str(interaction.user.id))
                    await interaction.response.send_message(
                        "Account binding updated.",
                        ephemeral=True
                    )
                else:
                    await self.discord_builder.bind_user_new(session, user.id, str(interaction.user.id))
                    await interaction.response.send_message(
                        "Account bound.",
                        ephemeral=True
                    )

            except UsernameIncorrect as e:
                logging.warning(e)
                await interaction.response.send_message(
                    f"Failed: *{e}*",
                    ephemeral=True
                )
            except UnmatchingPasswords as e:
                logging.warning(e)
                await interaction.response.send_message(
                    f"Failed: *{e}*",
                    ephemeral=True
                )

            finally:
                # Close Session
                await session.commit()
                await session.close()

    @account_bind_credentials.error
    async def on_account_bind_credentials_error(
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
    await client.add_cog(AccountBindCredentials(client))

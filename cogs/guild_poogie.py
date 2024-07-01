"""Extension module for GuildPoogie Cog."""
import logging

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import GuildBuilder
from core import BaseCog
from core.exceptions import (
    CoroutineFailed,
    MissingPermissions
)
from core.converters import poogie
from core.view import AppPoogieOutfits

class GuildPoogie(BaseCog):
    """Cog handling updating of guild poogie outfits."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.guild_builder = GuildBuilder()

    @app_commands.command(name="guild_poogie_set", description="Set guild poogie outfits.")
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.guild_poogie.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def guild_poogie_set(self, interaction: discord.Interaction, guild_id: int):
        """Set guild poogie outfits."""
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            try:
                if interaction.user.id not in CONFIG.discord.admin_user_ids:
                    raise MissingPermissions(
                        f"{interaction.user.mention} is missing permissions."
                    )

                guild = await self.guild_builder.select_poogie_outfits(session, guild_id)
                if not guild:
                    raise CoroutineFailed(
                        f"Guild `{guild_id}` doesn't exist."
                    )

                async def callback(pugi_outfits: int):
                    if not await self.guild_builder.update_poogie_outfits(
                        session,
                        guild_id,
                        pugi_outfits
                    ):
                        raise CoroutineFailed(
                            "Could not update table."
                        )

                my_int = guild.pugi_outfits
                my_bin = f'{my_int:09b}'[-9:]

                options = []
                for k in range(len(my_bin)):
                    element = my_bin[len(my_bin)-k-1]
                    options.append(
                        discord.SelectOption(
                            label=f"{poogie[k]}",
                            default=element=='1'
                        )
                    )

                await interaction.response.send_message(
                    view=AppPoogieOutfits(options, session=session, query_call=callback),
                    ephemeral=True
                )

            except (
                MissingPermissions
            ) as e:
                logging.warning("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Poogie Update Failed",
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
                        title="Poogie Update Failed",
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
                        title="Poogie Update Failed",
                        description=e,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

    @guild_poogie_set.error
    async def on_drop_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.guild_poogie.enabled:
        await client.add_cog(GuildPoogie(client))

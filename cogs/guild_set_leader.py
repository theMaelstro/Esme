import time

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import GuildBuilder

class GuildSetLeader(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.viewmodel = GuildBuilder()

    @app_commands.command(name="guild_set_leader", description="Set guild leader by id.")
    @app_commands.checks.cooldown(
    1,
    CONFIG.commands.realm.cooldown,
    key=lambda i: (i.guild_id, i.user.id)
    )
    async def guild_set_leader(
        self,
        interaction: discord.Interaction,
        guild_id: int,
        leader_id: int
    ):
        """Set guild leader by id."""
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            await self.viewmodel.update_guild_leader(self, guild_id, leader_id)

            # Close Session
            await session.commit()
            await session.close()

        await interaction.response.send_message(
            f'Beep Boop {interaction.user.mention}',
            ephemeral=True
        )

    @guild_set_leader.error
    async def on_guild_set_leader_error(
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
    await client.add_cog(GuildSetLeader(client))

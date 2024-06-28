"""
Extension module for BotManagement Cog.
Managment commands need bot mention message to work.
"""
import discord
from discord.ext import commands

from settings import CONFIG
from core import BaseCog
from core import MissingPermissions, CoroutineFailed

class BotManagement(BaseCog):
    """Cog handling bot admin tasks."""
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(pass_context=True)
    async def sync_commands(self, ctx, arg: discord.Guild) -> None:
        """Sync commands for specified guild."""
        try:
            if ctx.author.id not in CONFIG.discord.admin_user_ids:
                raise MissingPermissions(
                    f"{ctx.author.mention} is missing permissions."
                )

            self.client.tree.copy_global_to(guild=arg)
            await self.client.tree.clear_commands(guild=arg)
            await self.client.tree.sync(guild=arg)
            await ctx.send(
                embed=discord.Embed(
                    title="Commands Synced",
                    description=f"{ctx.author.mention} Guild: `{arg}` synced.",
                    color=discord.Color.green()
                ).set_author(
                    name=ctx.author.name,
                    icon_url=ctx.author.avatar.url
                )
            )

        except (
            MissingPermissions
        ) as e:
            await ctx.send(
                embed=discord.Embed(
                    title="Commands Sync Failed",
                    description=e,
                    color=discord.Color.red()
                ).set_author(
                    name=ctx.author.name,
                    icon_url=ctx.author.avatar.url
                )
            )

    @sync_commands.error
    async def on_sync_commands_error(
        self,
        ctx,
        error: commands.errors
    ):
        """On cooldown send remaining time info message."""
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    title="Commands Sync Failed",
                    description=(
                        "Missing required positional argument `guild_id`.\n"
                        f"{ctx.author.mention} Please use `sync_commands <guild_id>`."
                    ),
                    color=discord.Color.red()
                ).set_author(
                    name=ctx.author.name,
                    icon_url=ctx.author.avatar.url
                )
            )

    @commands.command(pass_context=True)
    async def sync(self, ctx) -> None:
        """Sync commands globally."""
        try:
            if ctx.author.id not in CONFIG.discord.admin_user_ids:
                raise MissingPermissions(
                    f"{ctx.author.mention} is missing permissions."
                )

            await self.client.tree.sync()
            await ctx.send(
                embed=discord.Embed(
                    title="Commands Synced",
                    color=discord.Color.green()
                ).set_author(
                    name=ctx.author.name,
                    icon_url=ctx.author.avatar.url
                )
            )

        except (
            MissingPermissions
        ) as e:
            await ctx.send(
                embed=discord.Embed(
                    title="Commands Sync Failed",
                    description=e,
                    color=discord.Color.red()
                ).set_author(
                    name=ctx.author.name,
                    icon_url=ctx.author.avatar.url
                )
            )

    @commands.command(pass_context=True)
    async def reload_cogs(self, ctx) -> None:
        """Reloads Cogs."""
        try:
            if ctx.author.id not in CONFIG.discord.admin_user_ids:
                raise MissingPermissions(
                    f"{ctx.author.mention} is missing permissions."
                )

            if not await self.client.reload_cogs():
                raise CoroutineFailed(
                    f"{ctx.author.mention} Could not reload cogs, coroutine failed."
                )

            await ctx.send(
                embed=discord.Embed(
                    title="Cogs Reloaded",
                    description=ctx.author.mention,
                    color=discord.Color.green()
                ).set_author(
                    name=ctx.author.name,
                    icon_url=ctx.author.avatar.url
                )
            )

        except (
            CoroutineFailed,
            MissingPermissions
        ) as e:
            await ctx.send(
                embed=discord.Embed(
                    title="Cogs Reload Failed",
                    description=e,
                    color=discord.Color.red()
                ).set_author(
                    name=ctx.author.name,
                    icon_url=ctx.author.avatar.url
                )
            )

    @commands.command(pass_context=True)
    async def reload_config(self, ctx):
        """Reload config file."""
        try:
            if ctx.author.id not in CONFIG.discord.admin_user_ids:
                raise MissingPermissions(
                    f"{ctx.author.mention} is missing permissions."
                )

            await CONFIG.init_config()
            await ctx.send(
                embed=discord.Embed(
                    title="Config Reloaded",
                    description=ctx.author.mention,
                    color=discord.Color.green()
                ).set_author(
                    name=ctx.author.name,
                    icon_url=ctx.author.avatar.url
                )
            )

        except (
            MissingPermissions
        ) as e:
            await ctx.send(
                embed=discord.Embed(
                    title="Config Reload Failed",
                    description=e,
                    color=discord.Color.red()
                ).set_author(
                    name=ctx.author.name,
                    icon_url=ctx.author.avatar.url
                )
            )

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(BotManagement(client))

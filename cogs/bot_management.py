import logging

import discord
from discord.ext import commands

from settings import CONFIG
from core import BaseCog

class BotManagement(BaseCog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=['?', 'list'], pass_context=True)
    async def list_commands(self, ctx):
        """List all prefix commands."""

        result = ""
        for element in self.client.walk_commands():
            result += f"`{element}`\n"

        if ctx.author.id in CONFIG.discord.admin_user_ids:
            await ctx.send(result)
        else:
            await ctx.send(f"You are not allowed to use that command {ctx.author.mention}.")

    @commands.command(pass_context=True)
    async def sync_commands(self, ctx, arg: discord.Guild) -> None:
        """Sync commands for specified guild."""
        if ctx.author.id not in CONFIG.discord.admin_user_ids:
            await ctx.send(f"You are not allowed to use that command {ctx.author.mention}.")
        else:
            if not arg:
                await ctx.send("No positional argument provided. `sync_commands guild_id`.")
            else:
                self.client.tree.copy_global_to(guild=arg)
                await self.client.tree.sync(guild=arg)
                await ctx.send(f"Synced commands for guild: {arg}.")

    @sync_commands.error
    async def on_register_error(
        self,
        ctx,
        error: commands.errors
    ):
        """On cooldown send remaining time info message."""
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(
                (
                    "# Error\n"
                    "## Trace: missing positional argument 'guild_id'\n"
                    f"{ctx.author.mention} Please use `sync_commands <guild_id>`"
                )
            )


    @commands.command(pass_context=True)
    async def reload_cogs(self, ctx) -> None:
        """Reloads Cogs."""
        if ctx.author.id in CONFIG.discord.admin_user_ids:
            if await self.client.reload_cogs():
                await ctx.send(
                    f'{ctx.author.mention}, Cogs Reloaded.', ephemeral=True
                )
        else:
            await ctx.send(
                f'{ctx.author.mention} you are not allowed to use this command.',
                ephemeral=True
            )

    @commands.command(pass_context=True)
    async def reload_config(self, ctx):
        """Reload config file."""
        if ctx.author.id in CONFIG.discord.admin_user_ids:
            await CONFIG.init_config()
            await ctx.send(
                'Config reloaded.'
            )
        else:
            await ctx.send(
                f"You are not allowed to use this command {ctx.author.mention}."
            )

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(BotManagement(client))

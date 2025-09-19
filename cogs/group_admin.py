import discord
from discord.ext import commands
from discord import app_commands

from settings import CONFIG
from core import BaseCog

from .partial_admin import (
    CharacterNameSet,
    GuildPoogie,
    Road
)

class AdminCog(BaseCog):
    """Cog handling guild applications."""
    def __init__(self, client: commands.Bot):
        self.client = client

    group_admin = app_commands.Group(
        name="admin",
        description="..."
    )
    group_check = app_commands.Group(
        name="check",
        parent = group_admin,
        description="..."
    )
    group_set = app_commands.Group(
        name="set",
        parent = group_admin,
        description="..."
    )

    @group_check.command(
        name="road",
        description="Checks the road stats of the given file."
    )
    async def admin_check_road(
        self,
        interaction: discord.Interaction,
        file: discord.Attachment
    ) -> None:
        """Checks the road stats of the given file."""
        partial_road_check = Road()
        await partial_road_check.check_road_stats(
            interaction,
            file
        )

    @group_set.command(
        name="charname",
        description="Set character name by ID."
    )
    async def admin_set_charname(
        self,
        interaction: discord.Interaction,
        character_int: int,
        new_name: app_commands.Range[str, 4, 12]
    ) -> None:
        """Set character name by ID."""
        partial_character_name_set = CharacterNameSet()
        await partial_character_name_set.set_charname(
            interaction,
            character_int,
            new_name
        )

    @group_set.command(
        name="poogie",
        description="Set guild poogie outfits by guild id."
    )
    async def admin_set_poogie(
        self,
        interaction: discord.Interaction,
        guild_id: int
    ) -> None:
        """Set guild poogie outfits by guild id."""
        partial_poogie_set = GuildPoogie()
        await partial_poogie_set.guild_poogie_set(
            interaction,
            guild_id
        )

    @admin_check_road.error
    @admin_set_poogie.error
    @admin_set_charname.error
    async def on_admin_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.features.cogs_groups.group_account.enabled:
        await client.add_cog(AdminCog(client))

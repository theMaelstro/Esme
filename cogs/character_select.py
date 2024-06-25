import time
import re
import logging

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import CharactersBuilder
from data import DiscordBuilder
from core.view.pagination_selector import PaginationSelector as Pagination
from core import get_weapon_type_image_url
from core.exceptions import (
    DiscordNotRegistered
)
from core import BaseCog

class CharacterSelect(BaseCog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.characters_builder = CharactersBuilder()
        self.discord_builder = DiscordBuilder()

    @app_commands.command(name="character_select", description="Select active character.")
    @app_commands.checks.cooldown(
    1,
    CONFIG.commands.realm.cooldown,
    key=lambda i: (i.guild_id, i.user.id)
    )
    async def character_select(self, interaction: discord.Interaction):
        """Select active character."""
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            try:
                # Check if user is registered.
                discord_user = await self.discord_builder.select_discord_user(
                    session, str(interaction.user.id)
                )
                if discord_user is None:
                    raise DiscordNotRegistered(
                        "No account registered for this discord user."
                    )

                elements = await self.characters_builder.select_characters_by_user_id(
                    session,
                    discord_user.user_id
                )
                selector_values = [character.id for character in elements]
                if isinstance(elements, list):
                    page_elements = 1
                    async def get_page(page: int):
                        emb = discord.Embed(title="Character List", description="", color=0x1E90FF)
                        offset = (page-1) * page_elements
                        for character in elements[offset:offset+page_elements]:
                            emb.description += (
                                f"**ID**: `{character.id}`\n"
                                f"**NAME**: `{re.escape(character.name)}`\n"
                                f"**LAST LOGIN**: <t:{round(character.last_login)}:f>\n"
                                #f"**TOTAL PLAYTIME**: `{'%04dH:%02dM' % (divmod(character.time_played, 60))}`\n"
                                #f"**WEAPON TYPE**: {get_weapon_type(character.weapon_type)}\n"
                                f"**KOURYOU POINTS**: `{character.kouryou_point}`\n"
                                f"**GC POINTS**: `{character.gcp}`\n"
                                f"**NETCAFE POINTS**: `{character.netcafe_points}`\n"
                            )
                            emb.set_thumbnail(url=get_weapon_type_image_url(character.weapon_type))
                        emb.set_author(
                            name=f"Requested by {interaction.user}",
                            icon_url=interaction.user.avatar.url
                        )
                        n = Pagination.compute_total_pages(len(elements), page_elements)
                        emb.set_footer(text=f"Page {page} from {n}")
                        return emb, n

                    await Pagination(
                        interaction,
                        session,
                        self.discord_builder.update_character,
                        selector_values,
                        get_page,
                        public=False
                    ).navegate()
                else:
                    await interaction.response.send_message("Error", ephemeral=True)

            except (
                DiscordNotRegistered
            ) as e:
                await interaction.response.send_message(
                    f"ERROR: {e}",
                    ephemeral=True
                )

    @character_select.error
    async def on_character_select_error(
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
    await client.add_cog(CharacterSelect(client))

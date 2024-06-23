import time
import re

import discord
from discord.ext import commands
from discord import app_commands

from settings import CONFIG
from data import CharactersBuilder
from core.view.pagination import Pagination
from core import get_weapon_type

class CharacterSelect(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.viewmodel = CharactersBuilder()

    @app_commands.command(name="character_select", description="Select active character.")
    @app_commands.checks.cooldown(
    1,
    CONFIG.commands.realm.cooldown,
    key=lambda i: (i.guild_id, i.user.id)
    )
    async def character_select(self, interaction: discord.Interaction, user_id: int):
        """Select active character."""

        elements = await self.viewmodel.select_characters_by_user_id(user_id)
        if isinstance(elements, list):
            L = 1
            async def get_page(page: int):
                emb = discord.Embed(title="Character List", description="", color=0x1E90FF)
                offset = (page-1) * L
                for character in elements[offset:offset+L]:
                    emb.description += (
                        f"**ID**: `{character.id}`\n"
                        f"**NAME**: `{re.escape(character.name)}`\n"
                        f"**LAST LOGIN**: <t:{round(character.last_login)}:f>\n"
                        #f"**TOTAL PLAYTIME**: `{'%04dH:%02dM' % (divmod(character.time_played, 60))}`\n"
                        f"**WEAPON TYPE**: {get_weapon_type(character.weapon_type)}\n"
                        f"**KOURYOU POINTS**: `{character.kouryou_point}`\n"
                        f"**GC POINTS**: `{character.gcp}`\n"
                        f"**NETCAFE POINTS**: `{character.netcafe_points}`\n"
                    )
                emb.set_author(
                    name=f"Requested by {interaction.user}",
                    icon_url=interaction.user.avatar.url
                )
                n = Pagination.compute_total_pages(len(elements), L)
                emb.set_footer(text=f"Page {page} from {n}")
                emb.set_thumbnail(url="http://vignette2.wikia.nocookie.net/monsterhunter/images/0/03/ItemIcon048.png/revision/latest?cb=20100611135527")
                return emb, n

            await Pagination(interaction, get_page, public=False).navegate()
        else:
            await interaction.response.send_message("Error", ephemeral=True)

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

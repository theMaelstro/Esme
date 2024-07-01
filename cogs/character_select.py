"""Extension module for AccountBindCredentials Cog."""
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
    CoroutineFailed,
    DiscordNotRegistered
)
from core import BaseCog

class CharacterSelect(BaseCog):
    """
    Cog handling active character selection.
    Mandatory for context commands.
    """
    def __init__(self, client: commands.Bot):
        self.client = client
        self.characters_builder = CharactersBuilder()
        self.discord_builder = DiscordBuilder()

    @app_commands.command(
        name="character_select",
        description="Select active character."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.character_select.cooldown,
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

                # Get character list.
                elements = await self.characters_builder.select_characters_by_user_id(
                    session,
                    discord_user.user_id
                )
                if not isinstance(elements, list):
                    raise CoroutineFailed(
                        "Query did not yield valid results."
                    )

                selector_values = [character.id for character in elements]
                page_elements = 1

                async def get_page(page: int):
                    emb = discord.Embed(
                        description="",
                        color=discord.Color.green()
                    )
                    offset = (page-1) * page_elements
                    for character in elements[offset:offset+page_elements]:
                        emb.title = re.escape(character.name)
                        emb.add_field(
                            name = 'ID',
                            value = character.id,
                            inline = False
                        )
                        emb.add_field(
                            name = 'LAST LOGIN',
                            value = f"<t:{round(character.last_login)}:f>",
                            inline = False
                        )
                        emb.add_field(
                            name = 'KP',
                            value = character.kouryou_point,
                            inline = True
                        )
                        emb.add_field(
                            name = 'GCP',
                            value = character.gcp,
                            inline = True
                        )
                        emb.add_field(
                            name = 'NP',
                            value = character.netcafe_points,
                            inline = True
                        )
                        # TODO: Figure out what time_played is.
                        #emb.add_field(
                        #    name = 'TIME PLAYED',
                        #    value = f"{'%04dH:%02dM' % (divmod(character.time_played, 60))}",
                        #    inline=True
                        #)

                        emb.set_thumbnail(url=get_weapon_type_image_url(character.weapon_type))
                        emb.set_author(
                            name=f"{interaction.user} characters.",
                            icon_url=interaction.user.avatar.url
                        )
                    n = Pagination.compute_total_pages(len(elements), page_elements)
                    emb.set_footer(text=f"Page {page} from {n}")
                    return emb, n

                logging.info("%s: %s", interaction.user.id, "Character Select Open")
                await Pagination(
                    interaction,
                    session,
                    self.discord_builder.update_character,
                    selector_values,
                    get_page,
                    public=False,
                ).navegate()

            except (
                DiscordNotRegistered
            ) as e:
                logging.warning("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Character Select Failed",
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
                        title="Character Select Failed",
                        description=e,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

    @character_select.error
    async def on_character_select_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.character_select.enabled:
        await client.add_cog(CharacterSelect(client))

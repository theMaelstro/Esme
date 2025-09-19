"""Extension module for AccountBindCredentials Cog."""
import re
import logging

import discord
from sqlalchemy.ext.asyncio import async_sessionmaker

from data.connector import CONN
from data import CharactersBuilder
from data import DiscordBuilder

from settings import CONFIG
from core.view.pagination_selector import PaginationSelector as Pagination
from core import get_weapon_type_image_url
from core.exceptions import (
    CoroutineFailed,
    DiscordNotRegistered,
    MissingPermissions
)

class CharacterSelect():
    def __init__(self):
        self.character_builder = CharactersBuilder()
        self.discord_builder = DiscordBuilder()

    async def character_select(self, interaction: discord.Interaction):
        """Select active character."""
        try:
            if not CONFIG.check_permission(
                CONFIG.commands.account_character_select.permission,
                interaction.user
            ):
                raise MissingPermissions(
                    f"{interaction.user.mention} is missing permissions to use command."
                )

            # Create session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                # Check if user is registered.
                discord_user = await self.discord_builder.select_discord_user(
                    session, str(interaction.user.id)
                )
                if discord_user is None:
                    raise DiscordNotRegistered(
                        "No account registered for this discord user."
                    )

                # Get character list.
                elements = await self.character_builder.select_characters_by_user_id(
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
                            inline = True
                        )
                        emb.add_field(
                            name = 'HR',
                            value = character.hr,
                            inline = True
                        )
                        emb.add_field(
                            name = 'GR',
                            value = character.gr,
                            inline = True
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
                            name=f"{interaction.user} characters",
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
            DiscordNotRegistered,
            MissingPermissions
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
                    description="Internal Error",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

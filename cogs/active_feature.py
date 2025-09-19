"""Extension module for example Ping Cog with response interaction."""
import logging
from datetime import datetime

import discord
from discord.ext import commands
from discord import app_commands

from sqlalchemy.ext.asyncio import async_sessionmaker

from data.connector import CONN
from data import (
    UniversalBuilder
)

from settings import CONFIG
from core import (
    BaseCog,
    ApplicationEmojis
)
from core.exceptions import (
    CoroutineFailed,
    MissingPermissions
)

def get_weapon_emoji_string(
    emojis: ApplicationEmojis,
    mask: list
) -> str:
    return (
        f"{emojis.get_sword_shield(mask[9])}"
        f"{emojis.get_dual_blades(mask[7])}"
        f"{emojis.get_great_sword(mask[13])}"
        f"{emojis.get_long_sword(mask[6])}"
        f"{emojis.get_hammer(mask[11])}"
        f"{emojis.get_hunting_horn(mask[5])}"
        f"{emojis.get_lance(mask[10])}"
        f"{emojis.get_gunlance(mask[4])}"
        f"{emojis.get_switch_axe(mask[1])}"
        f"{emojis.get_tonfa(mask[2])}"
        f"{emojis.get_magnet_spike(mask[0])}"
        f"{emojis.get_light_bowgun(mask[8])}"
        f"{emojis.get_heavy_bowgun(mask[12])}"
        f"{emojis.get_bow(mask[3])}"
    )

class ActiveFeature(BaseCog):
    """Cog handling weapon feature display."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.universal_builder = UniversalBuilder()

    @app_commands.command(
        name="features",
        description="List active weapon features."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.features.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def features(self, interaction: discord.Interaction):
        """Display features list"""
        try:
            if not CONFIG.check_permission(
                CONFIG.commands.features.permission,
                interaction.user
            ):
                raise MissingPermissions(
                    f"{interaction.user.mention} is missing permissions to use command."
                )

            # Create session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                features = await self.universal_builder.get_active_feature(session)
                if not features:
                    raise CoroutineFailed()

                features_current = f"{features[-1].featured:b}".zfill(14)
                #features_current_time = round((features[-1].start_time).timestamp())
                features_next = f"{features[-2].featured:b}".zfill(14)
                #features_next_time = round((features[-2].start_time).timestamp())
                features_next2 = f"{features[-3].featured:b}".zfill(14)
                #features_next_time2 = round((features[-3].start_time).timestamp())
                logging.info("%s: %s", interaction.user.id, "Ping!")
                emojis = await self.client.fetch_application_emojis()
                emojis = ApplicationEmojis(emojis)
                await interaction.response.send_message(
                    ephemeral=True,
                    content=(
                        "## Active Feature\n"
                        #f"<t:{features_current_time}:R>\n"
                        f"# {get_weapon_emoji_string(emojis, features_current)}\n"
                        "## Next Feature\n"
                        #f"<t:{features_next_time}:R>\n"
                        f"# {get_weapon_emoji_string(emojis, features_next)}\n"
                        #f"<t:{features_next_time2}:R>\n"
                        f"# {get_weapon_emoji_string(emojis, features_next2)}\n"
                    )
                )

        except (
            MissingPermissions
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Weapon Feature",
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
                    title="Weapon Feature",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @features.error
    async def on_features_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.features.enabled:
        await client.add_cog(ActiveFeature(client))

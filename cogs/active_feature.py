"""Extension module for example Ping Cog with response interaction."""
import logging
from datetime import datetime, timedelta, timezone

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

                now = datetime.now(timezone.utc)
                emojis = await self.client.fetch_application_emojis()
                emojis = ApplicationEmojis(emojis)
                valid_features = []
                features_str = ""
                for feature in reversed(features):
                    if (
                        ((now - feature.start_time).total_seconds() / 3600)
                    <= 24 + CONFIG.erupe.timestamp_offset):
                        valid_features.append(feature)

                for k, feature in enumerate(valid_features):
                    my_f = f"{feature.featured:b}".zfill(14)
                    if k == 0:
                        features_str += (
                            "## Active Feature\n"
                            f"# {get_weapon_emoji_string(emojis, my_f)}\n"
                        )
                    if k == 1:
                        features_str += (
                            "## Next Feature\n"
                            f"# {get_weapon_emoji_string(emojis, my_f)}\n"
                        )
                    if k > 1:
                        features_str += (
                            f"# {get_weapon_emoji_string(emojis, my_f)}\n"
                        )
                logging.info("%s: %s", interaction.user.id, "Active Feature opened.")
                await interaction.response.send_message(
                    ephemeral=True,
                    content=features_str
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

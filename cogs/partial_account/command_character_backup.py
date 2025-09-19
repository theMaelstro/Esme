"""Extension module for SetPsn Cog."""
import io
import zipfile
import logging
from datetime import datetime, timezone, timedelta

import discord
from sqlalchemy.ext.asyncio import async_sessionmaker

from data.connector import CONN
from data import (
    CharactersBuilder,
    DiscordBuilder
)

from settings import CONFIG
from core.exceptions import (
    CoroutineFailed,
    CommandOnCooldown,
    CharacterNotSet,
    DiscordNotRegistered,
    MissingPermissions
)

def get_days(
    current_stamp: int,
    reference_stamp: int
) -> int:
    """Get days difference from timestamps."""
    return (
        datetime.fromtimestamp(
            current_stamp
        )-datetime.fromtimestamp(
            reference_stamp
        )
    ).days

class CharacterBackup():
    """Cog handling new user character creation."""
    def __init__(self):
        self.character_builder = CharactersBuilder()
        self.discord_builder = DiscordBuilder()

    async def character_backup(
        self,
        interaction: discord.Interaction
    ):
        """Create player character."""
        try:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Backup Started",
                    description=(
                    "Please wait while backup is in process. "
                    "Make sure your dms are enabled."
                    ),
                    color=discord.Color.blue()
                ),
                ephemeral=True
            )
            if not CONFIG.check_permission(
                CONFIG.commands.account_character_backup.permission,
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
                    session,
                    str(interaction.user.id)
                )

                if discord_user is None:
                    raise DiscordNotRegistered(
                        "No account registered for this discord user."
                    )

                cooldown = await self.discord_builder.get_cooldown(
                    session,
                    interaction.user.id
                )
                time_now = round(datetime.now(timezone.utc).timestamp())
                if cooldown:
                    days_since = get_days(
                        time_now,
                        cooldown.cd_backup
                    )
                    expiry_date = (
                        datetime.fromtimestamp(cooldown.cd_backup)
                        + timedelta(days=CONFIG.commands.account_character_backup.hard_cooldown)
                    ).timestamp()
                    if days_since < CONFIG.commands.account_character_backup.hard_cooldown:
                        raise CommandOnCooldown(
                            f"Cooldown not expired. Try again <t:{round(expiry_date)}:R>"
                        )

                # Get character list.
                character = await self.character_builder.select_character_details_by_character_id(
                    session,
                    discord_user.character_id
                )
                if character is None:
                    raise CharacterNotSet(
                        "No character selected. Please use `/account character select` command."
                    )

                data = await self.character_builder.get_character_save(
                    session,
                    discord_user.character_id
                )

                zip_buffer = io.BytesIO()
                zf = zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False)

                for file in data.files:
                    if file.file_data:
                        zf.writestr(f"{file.file_name}.bin", file.file_data)
                zf.close()

                for zfile in zf.filelist:
                    zfile.create_system = 0
                zip_buffer.seek(0)

                await interaction.user.send(
                    embed=discord.Embed(
                        title="Save Backup",
                        color=discord.Color.green()
                    ),
                    file=discord.File(zip_buffer, "savedata.zip")
                )

                zip_buffer.seek(0)
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Save Backup Sent",
                        description="Check direct messages for permanent attachment.",
                        color=discord.Color.green()
                    ),
                    file=discord.File(zip_buffer, "savedata.zip"),
                    ephemeral=True
                )

                if not await self.discord_builder.update_cooldown(
                    session,
                    interaction.user.id,
                    "backup",
                    time_now
                ):
                    raise CoroutineFailed()

                # Close Session
                await session.commit()
                await session.close()

        except (
            CommandOnCooldown,
            CharacterNotSet,
            DiscordNotRegistered,
            MissingPermissions
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Character Backup Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        except (
            CoroutineFailed
        ) as e:
            logging.error("%s: %s", interaction.user.id, e)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Character Backup Failed",
                    description="Internal Error",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

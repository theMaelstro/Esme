"""Extension module for Road Cog."""
import logging

import discord
from discord.ext import commands

from sqlalchemy.ext.asyncio import async_sessionmaker

from settings import CONFIG
from data.connector import CONN
from data import CharactersBuilder
from core.exceptions import (
    CoroutineFailed,
    MissingPermissions,
    InvalidArgument
)
from core.binary_handler import (
    compress,
    decompress,
    CharacterData
)

class CharacterNameSet():
    """Cog handling reading road progress data."""
    def __init__(self):
        self.character_builder = CharactersBuilder()

    async def set_charname(
        self,
        interaction: discord.Interaction,
        character_id: int,
        name: str
    ):
        """Check rengoku save file."""
        try:
            if not CONFIG.check_permission(
                CONFIG.commands.road_check.permission,
                interaction.user
            ):
                raise MissingPermissions(
                    f"{interaction.user.mention} is missing permissions."
                )

            # Create session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                data = await self.character_builder.get_character_save(session, character_id)

                if not data.savedata.file_data:
                    raise InvalidArgument(
                        "No valid data found. Check character id."
                    )
                character = CharacterData(decompress(data.savedata.file_data))
                character.set_name(name)
                c = compress(character.save_data)

                if not await self.character_builder.update_character_save(
                    session,
                    character_id,
                    c
                ):
                    raise CoroutineFailed(
                        "Could not update character save."
                    )

                if not await self.character_builder.update_character_name(
                    session,
                    character_id,
                    name
                ):
                    raise CoroutineFailed(
                        "Could not update character save."
                    )

                await session.commit()
                await session.close()

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Name Changed",
                    color=discord.Color.green()
                ),
                ephemeral=True
            )

        except (
            InvalidArgument
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Name Change Failed",
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
                        title="Name Change Failed",
                        description="Internal Error. Check logs.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

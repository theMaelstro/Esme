"""Extension module for SetPsn Cog."""
import traceback
import logging

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
    CharacterExists,
    UserNotBound,
    MissingPermissions,
    TermsRejected
)

class CharacterCreate():
    """Cog handling new user character creation."""
    def __init__(self):
        self.character_builder = CharactersBuilder()
        self.discord_builder = DiscordBuilder()

    async def character_create(
        self,
        interaction: discord.Interaction
    ):
        """Create player character."""
        try:
            if not CONFIG.check_permission(
                CONFIG.commands.account_character_create.permission,
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
                    raise TermsRejected()

                meta = await self.discord_builder.select_meta(
                    session,
                    "terms"
                )

                if discord_user.terms != meta['sha']:
                    raise TermsRejected()

                if discord_user.user_id is None:
                    raise UserNotBound(
                        "No account registered for this discord user."
                    )

                if await self.character_builder.select_characters_by_user_id(
                    session, discord_user.user_id
                ):
                    raise CharacterExists(
                        "Character already exists for this discord user."
                    )

                await self.character_builder.create_character(
                    session,
                    discord_user.user_id
                )

                logging.info("%s: %s", interaction.user.id, "Character Created")
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Character Created",
                        description="Check game launcher.",
                        color=discord.Color.green()
                    ),
                    ephemeral=True
                )

                # Commit
                await session.commit()
                await session.close()

        except (
            CharacterExists,
            UserNotBound,
            MissingPermissions
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Character Creation Failed",
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
                    title="Character Creation Failed",
                    description="Internal Error",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        except (
            TermsRejected
        ) as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Character Creation Failed",
                    description=e.readable,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        except (
            Exception
        ) as e:
            logging.error("%s: %s %s %s", interaction.user.id, type(e), e, traceback.format_exc())
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Procesing Failed",
                    description="Internal Error.",
                    color=discord.Color.red()
                ),
                view=None
            )

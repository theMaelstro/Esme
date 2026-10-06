"""Extension module allowing display of software license."""
import logging
import base64
import traceback

import discord
from discord.ext import commands
from discord import app_commands

from sqlalchemy.ext.asyncio import async_sessionmaker
from data.connector import CONN
from data import (
    DiscordBuilder
)

from core import BaseCog
from core.exceptions import (
    HTTPServerUnreachable,
    LicenseNotFound
)

from core.view.pagination import Pagination

class License(BaseCog):
    """Cog example with basic interaction response."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.discord_builder = DiscordBuilder()

    @app_commands.command(
        name="license",
        description="Display software license."
    )
    @app_commands.checks.cooldown(
        1,
        5.0,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def license(self, interaction: discord.Interaction):
        """Display license."""
        try:
            # Start session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:

                data = await self.discord_builder.select_meta(
                    session,
                    "license"
                )
                if data is None:
                    raise LicenseNotFound(
                        "Couldnt find license."
                    )

                content = data['content']

                match data["encoding"]:
                    case "base64":
                        content = base64.b64decode(content).decode("utf-8")
                content: str = content + (
                    f"\nThis license is available in source repository at {data['html_url']}"
                    + f"\nRevision: `{data['sha']}`"
                    + "\nSoftware is available at https://github.com/theMaelstro/Esme"
                )

                # Close Session
                await session.commit()
                await session.close()

            text_split = content.split("\n\n")
            char_limit = 2500
            page_contents = []
            k = 0
            for element in text_split:
                if len(page_contents) == k+1:
                    if (len(page_contents[k]) + len(element)) >= char_limit:
                        k += 1
                if len(page_contents) <= k :
                    page_contents.append(element)
                else:
                    if (len(page_contents[k]) + len(element)) < char_limit:
                        page_contents[k] += ("\n\n" + element)

            async def get_page(page: int):
                emb = discord.Embed(
                    title="LICENSE",
                    description=page_contents[page-1],
                    color=discord.Color.blue()
                )

                n = len(page_contents)
                emb.set_footer(text=f"Page {page} from {n}")
                return emb, n

            await Pagination(interaction, get_page, public=False).navegate()

        except (
            HTTPServerUnreachable
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="License Display Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        except Exception as e:
            logging.error("%s: %s %s %s", interaction.user.id, type(e), e, traceback.format_exc())
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="License Display Failed",
                    description="Internal Error",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @license.error
    async def on_license_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(License(client))

"""Extension module to handle terms of service."""
import logging
import base64
import traceback
from typing import Callable, Optional

import discord
from discord.ext import commands
from discord import app_commands

from sqlalchemy.ext.asyncio import async_sessionmaker
from data.connector import CONN
from data import (
    DiscordBuilder
)

from settings import CONFIG

from core import BaseCog
from core.exceptions import (
    CoroutineFailed,
    HTTPServerUnreachable,
    TermsNotFound,
    TermsRejected
)

class Pagination(discord.ui.View):
    """
    Pagination handling terms of service with 5 buttons.
    """
    def __init__(
        self,
        interaction: discord.Interaction,
        get_page: Callable,
        checksum: str,
        public = True
    ):
        self.interaction = interaction
        self.get_page = get_page
        self.public = not public
        self.checksum = checksum
        self.total_pages: Optional[int] = None
        self.index = 1
        self.discord_builder = DiscordBuilder()
        super().__init__(timeout=360)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check view owner."""
        if interaction.user == self.interaction.user:
            return True

        emb = discord.Embed(
            description="Only the author of the command can perform this action.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(
            embed=emb,
            ephemeral=True
        )
        return False

    async def navegate(self):
        "Handle page controls."
        emb, self.total_pages = await self.get_page(self.index)
        if self.total_pages == 1:
            await self.interaction.response.send_message(
                embed=emb,
                ephemeral=self.public
            )
        elif self.total_pages > 1:
            self.update_buttons()
            await self.interaction.response.send_message(
                embed=emb,
                view=self,
                ephemeral=self.public
            )

    async def edit_page(self, interaction: discord.Interaction):
        "Update page contents."
        emb, self.total_pages = await self.get_page(self.index)
        self.update_buttons()
        await interaction.response.edit_message(
            embed=emb,
            view=self
        )

    def update_buttons(self):
        "Update buttons state on page change."
        self.children[0].disabled = self.index == 1
        self.children[1].disabled = self.index == self.total_pages
        self.children[2].disabled = self.index == 1
        self.children[4].disabled = self.index != self.total_pages

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: discord.Button):
        "Previous page."
        self.index -= 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        "Next page."
        self.index += 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.blurple)
    async def end(self, interaction: discord.Interaction, button: discord.Button):
        self.index = 1
        await self.edit_page(interaction)

    @discord.ui.button(
        label="Decline",
        style=discord.ButtonStyle.danger
    )
    async def decline(self, interaction: discord.Interaction, button: discord.Button):
        "Decline Terms."
        try:
            # Start session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                # Check if user is registered.
                discord_user = await self.discord_builder.select_discord_user(
                    session, str(interaction.user.id)
                )

                if discord_user is not None:
                    # Update User
                    if not await self.discord_builder.update_user_terms(
                        session,
                        str(interaction.user.id),
                        None
                    ):
                        raise CoroutineFailed(
                            "Could not update table."
                        )

                # Close Session
                await session.commit()
                await session.close()

            raise TermsRejected()

        except TermsRejected as e:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title=e,
                    description=e.readable,
                    color=discord.Color.blue()
                ),
                view=None
            )

        except (
            CoroutineFailed
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

        except Exception as e:
            logging.error("%s: %s %s %s", interaction.user.id, type(e), e, traceback.format_exc())
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Procesing Failed",
                    description="Internal Error.",
                    color=discord.Color.red()
                ),
                view=None
            )

    @discord.ui.button(
        label="Accept",
        disabled=True,
        style=discord.ButtonStyle.success
    )
    async def accept(self, interaction: discord.Interaction, button: discord.Button):
        "Accept Terms."
        try:
            # Start session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                # Check if user is registered.
                discord_user = await self.discord_builder.select_discord_user(
                    session, str(interaction.user.id)
                )

                if discord_user is not None:
                    # Update User
                    if not await self.discord_builder.update_user_terms(
                        session,
                        str(interaction.user.id),
                        self.checksum
                    ):
                        raise CoroutineFailed(
                            "Could not update table."
                        )

                else:
                    # Register User
                    await self.discord_builder.create_user_entry(
                        session,
                        str(interaction.user.id),
                        self.checksum
                    )

                # Close Session
                await session.commit()
                await session.close()

            logging.info("%s: %s", interaction.user.id, "Terms Accepted")
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Terms Accepted",
                    description=(
                        "\n\nIn case you want to withdraw the agreement and delete **account bind data** please use `/delete` command." +
                        "\n\nIf you wish to review these **Terms of Service** again use `/terms` command." +
                        "\n\nIf you haven't bound you can proceed to binding process with `/account bind` commands."
                    ),
                    color=discord.Color.green()
                ),
                view=None
            )

        except (
            CoroutineFailed
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

        except Exception as e:
            logging.error("%s: %s %s %s", interaction.user.id, type(e), e, traceback.format_exc())
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Procesing Failed",
                    description="Internal Error.",
                    color=discord.Color.red()
                ),
                view=None
            )

    async def on_timeout(self):
        # remove buttons on timeout
        message = await self.interaction.original_response()
        await message.edit(view=None)

class Terms(BaseCog):
    """Cog example with basic interaction response."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.discord_builder = DiscordBuilder()

    @app_commands.command(
        name="terms",
        description="Display Terms of Service."
    )
    @app_commands.checks.cooldown(
        1,
        5.0,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def terms(self, interaction: discord.Interaction):
        """Display terms."""
        try:
            # Start session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:

                data = await self.discord_builder.select_meta(
                    session,
                    "terms"
                )
                if data is None:
                    raise TermsNotFound(
                        "Couldnt find terms."
                    )

                content = data['content']

                match data["encoding"]:
                    case "base64":
                        content = base64.b64decode(content).decode("utf-8")
                content: str = content + (
                    f"\nThese terms are available at {data['html_url']}" +
                    f"\nRevision: `{data['sha']}`"
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
                    title="Terms of Service",
                    description=page_contents[page-1],
                    color=discord.Color.blue()
                )

                n = len(page_contents)
                emb.set_footer(text=f"Page {page} from {n}")
                return emb, n

            await Pagination(
                interaction,
                get_page,
                data['sha'],
                public=False
            ).navegate()

        except (
            HTTPServerUnreachable,
            TermsNotFound
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Terms Display Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        except Exception as e:
            logging.error("%s: %s %s %s", interaction.user.id, type(e), e, traceback.format_exc())
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Terms Display Failed",
                    description="Internal Error",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @terms.error
    async def on_terms_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(Terms(client))

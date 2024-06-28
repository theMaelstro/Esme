"""Extension module for GuildPoogie Cog."""
import logging
from typing import Callable

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from settings import CONFIG
from data.connector import CONN
from data import GuildBuilder
from core import BaseCog
from core import (
    CoroutineFailed,
    MissingPermissions
)

poogie = {
    0: "Naked Emperor",
    1: "Soporific White",
    2: "Black Green Clash",
    3: "Silent Suit",
    4: "Bewitching Pink",
    5: "Nostalgic Stripe",
    6: "Soothing Sky",
    7: "Gentle Green",
    8: "Restless Brown"
}

class DynamicSelect(discord.ui.Select):
    def __init__(
            self,
            options: list,
            respone: Callable
        ) -> None:
        super().__init__(
            placeholder="Select Outfits",
            min_values=0,
            max_values=len(options),
            options=options
        )
        self.response = respone

    async def callback(self, interaction: discord.Interaction):
        #await interaction.response.edit_message(content=f"Selected {self.values}")
        bin_num = ""
        for key, value in poogie.items():
            bin_num = f"{value in self.values:d}{bin_num}"
        try:
            await self.response(int(bin_num, base=2))
        except (
            CoroutineFailed
        ) as e:
            logging.error("%s: %s", interaction.user.id, e)
            await interaction.response.edit_message(
                view=self.view,
                embed=discord.Embed(
                    title="Poogie Update Failed",
                    description=e,
                    color=discord.Color.red()
                )
            )

        logging.info("%s: %s", interaction.user.id, "Poogie Outfits Updated")
        await interaction.response.edit_message(
            view=self.view,
            embed=discord.Embed(
                title="Poogie Outfits Updated",
                description=f"{int(bin_num, base=2)}",
                color=discord.Color.green()
            )
        )

class DynamicSelectView(discord.ui.View):
    def __init__(
            self,
            options: list,
            *,
            timeout = 60,
            session: async_sessionmaker[AsyncSession],
            query_call: Callable
        ):
        super().__init__(timeout=timeout)
        self.add_item(DynamicSelect(options, self.response))
        self.session = session
        self.query_call = query_call

    async def response(self, query_value):
        if self.query_call:
            await self.query_call(query_value)
        await self._close_session()
        self._disable_all()

    async def _close_session(self):
        if self.session:
            # Close Session
            logging.info("%s", "Poogie Session Closed.")
            await self.session.commit()
            await self.session.close()

    def _disable_all(self) -> None:
        for item in self.children:
            print(item.__class__, isinstance(item, (discord.ui.Button, DynamicSelect)))
            if isinstance(item, (discord.ui.Button, DynamicSelect)):
                self.remove_item(item)

    async def on_timeout(self) -> None:
        # disable all components
        await self._close_session()
        self._disable_all()

class GuildPoogie(BaseCog):
    """Cog handling updating of guild poogie outfits."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.guild_builder = GuildBuilder()

    @app_commands.command(name="guild_poogie_set", description="Set guild poogie outfits.")
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.realm.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    async def guild_poogie_set(self, interaction: discord.Interaction, guild_id: int):
        """Set guild poogie outfits."""
        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            try:
                if interaction.user.id not in CONFIG.discord.admin_user_ids:
                    raise MissingPermissions(
                        f"{interaction.user.mention} is missing permissions."
                    )

                guild = await self.guild_builder.select_poogie_outfits(session, guild_id)
                if not guild:
                    raise CoroutineFailed(
                        f"Guild `{guild_id}` doesn't exist."
                    )

                async def callback(pugi_outfits: int):
                    if not await self.guild_builder.update_poogie_outfits(
                        session,
                        guild_id,
                        pugi_outfits
                    ):
                        raise CoroutineFailed(
                            "Could not update table."
                        )

                my_int = guild.pugi_outfits
                my_bin = f'{my_int:09b}'

                options = []
                for k in range(len(my_bin)):
                    element = my_bin[len(my_bin)-k-1]
                    options.append(
                        discord.SelectOption(
                            label=f"{poogie[k]}",
                            default=element=='1'
                        )
                    )

                await interaction.response.send_message(
                    view=DynamicSelectView(options, session=session, query_call=callback),
                    ephemeral=True
                )

            except (
                CoroutineFailed,
                MissingPermissions
            ) as e:
                logging.warning("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Poogie Update Failed",
                        description=e,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

            except (
                Exception
            ) as e:
                logging.error("%s: %s", interaction.user.id, e)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Poogie Update Failed",
                        description=e,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )

    @guild_poogie_set.error
    async def on_drop_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(GuildPoogie(client))

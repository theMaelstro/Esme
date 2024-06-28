"""
Holds main Poogie view with its helper ui elements.
"""
import logging
from typing import Callable

import discord
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from core.exceptions import (
    CoroutineFailed,
)
from core.converters import poogie

class DynamicSelect(discord.ui.Select):
    """Dynamic poogie outfit Selection Menu"""
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
        for _, value in poogie.items():
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

class AppPoogieOutfits(discord.ui.View):
    """Main Poogie Outfit selection View."""
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
        """Response callback function for selection menu."""
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
            if isinstance(item, (discord.ui.Button, DynamicSelect)):
                self.remove_item(item)

    async def on_timeout(self) -> None:
        # disable all components
        await self._close_session()
        self._disable_all()

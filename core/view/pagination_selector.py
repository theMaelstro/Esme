from typing import Any, Callable
import discord

from .pagination import Pagination

class PaginationSelector(Pagination):
    def __init__(
            self,
            interaction: discord.Interaction[discord.Client],
            session,
            method_call,
            selector_values: list[int],
            get_page: Callable[..., Any],
            public=True,
        ):
        super().__init__(interaction, get_page, public)
        self.session = session
        self.method_call = method_call
        self.selector_values = selector_values

    # Override navegate func to always show buttons.
    async def navegate(self):
        emb, self.total_pages = await self.get_page(self.index)
        self.update_buttons()
        await self.interaction.response.send_message(embed=emb, view=self, ephemeral=self.public)

    # Override button update.
    def update_buttons(self):
        if self.total_pages == 1:
            self.children[2].disabled = True
        if self.index > self.total_pages // 2:
            self.children[2].emoji = "⏮️"
        else:
            self.children[2].emoji = "⏭️"
        self.children[0].disabled = self.index == 1
        self.children[1].disabled = self.index == self.total_pages

    async def callback(self, interaction: discord.Interaction):
        # Call function
        await self.method_call(
            self.session,
            self.selector_values[self.index-1],
            str(interaction.user.id)
        )
        # Close session
        await self.session.commit()
        await self.session.close()
        # Disable buttons
        for child in self.children:
            child.disabled = True
        # Prepare response embed
        emb = discord.Embed(
            title="Character Selected",
            color=0x00FF00
        )
        emb.set_author(
            name=f"Requested by {interaction.user}",
            icon_url=interaction.user.avatar.url
        )
        #emb.set_footer(text=f"Page {page} from {n}")

        # Update embed
        await interaction.response.edit_message(embed=emb, view=self)

    @discord.ui.button(emoji="✅", style=discord.ButtonStyle.blurple)
    async def select(self, interaction: discord.Interaction, button: discord.Button):
        await self.callback(interaction)

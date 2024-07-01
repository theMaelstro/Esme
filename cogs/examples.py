"""
discord.py documentation examples put into cog.
https://github.com/Rapptz/discord.py/blob/master/examples/app_commands/basic.py

"""

from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands

from settings import CONFIG
from core import BaseCog

class Examples(BaseCog):
    """Cog which contains discord.py documentation examples."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.ctx_menu_show_join_date = app_commands.ContextMenu(
            name='Show Join Date',
            callback = self.show_join_date,
        )
        self.client.tree.add_command(self.ctx_menu_show_join_date)

        self.ctx_menu_report_message = app_commands.ContextMenu(
            name='Report to Moderators',
            callback = self.report_message,
        )
        self.client.tree.add_command(self.ctx_menu_report_message)

    @app_commands.command(name="hello", description="Says hello!")
    async def hello(self, interaction: discord.Interaction):
        """Says hello!"""
        await interaction.response.send_message(f'Hi, {interaction.user.mention}', ephemeral=True)

    @app_commands.command(name="add", description="Adds two numbers together.")
    @app_commands.describe(
    first_value='The first value you want to add something to',
    second_value='The value you want to add to the first value',
    )
    async def add(self, interaction: discord.Interaction, first_value: int, second_value: int):
        """Adds two numbers together."""
        await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')

    # The rename decorator allows us to change the display of the parameter on Discord.
    # In this example, even though we use `text_to_send` in the code, the client will use `text` instead.
    # Note that other decorators will still refer to it as `text_to_send` in the code.
    @app_commands.command(name="send", description="Sends the text into the current channel.")
    @app_commands.rename(text_to_send='text')
    @app_commands.describe(text_to_send='Text to send in the current channel')
    async def send(self, interaction: discord.Interaction, text_to_send: str):
        """Sends the text into the current channel."""
        await interaction.response.send_message(text_to_send)

    # To make an argument optional, you can either give it a supported default argument
    # or you can mark it as Optional from the typing standard library. This example does both.
    @app_commands.command(name="joined", description="Says when a member joined.")
    @app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
    async def joined(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Says when a member joined."""
        # If no member is explicitly provided then we use the command user here
        member = member or interaction.user

        # The format_dt function formats the date time into a human readable representation in the official client
        await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')

    # A Context Menu command is an app command that can be run on a member or on a message by
    # accessing a menu within the client, usually via right clicking.
    # It always takes an interaction as its first parameter and a Member or Message as its second parameter.

    # This context menu command only works on members
    
    async def show_join_date(self, interaction: discord.Interaction, member: discord.Member):
        """Show user join date."""
        # The format_dt function formats the date time into a human readable representation in the official client
        await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')

    # This context menu command only works on messages
    async def report_message(self, interaction: discord.Interaction, message: discord.Message):
        """Report message to moderators."""
        # We're sending this response message with ephemeral=True, so only the command executor can see it
        await interaction.response.send_message(
            f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
        )

        # Handle report by sending it into a log channel
        log_channel = interaction.guild.get_channel(CONFIG.discord.logs_channel_id)  # replace with your channel id

        embed = discord.Embed(title='Reported Message')
        if message.content:
            embed.description = message.content

        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.timestamp = message.created_at

        url_view = discord.ui.View()
        url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

        await log_channel.send(embed=embed, view=url_view)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    #await client.add_cog(Examples(client))

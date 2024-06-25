"""
Main Module
"""
import os
import logging

from dotenv import load_dotenv
import discord
from discord.ext import commands

from settings.logger import init_logger
from settings import CONFIG
from data.connector import CONN

init_logger()
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MyClient(commands.Bot):
    """Class representing bot client."""
    # pylint: disable=redefined-outer-name
    def __init__(self, *, intents: discord.Intents):
        super().__init__(
            command_prefix=commands.when_mentioned,
            activity=discord.CustomActivity('Petting Palicos'),
            intents=intents
        )
    #def __init__(self):
    #    super().__init__(command_prefix=commands.when_mentioned, intents=discord.Intents.default())

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def load_cogs(self):
        """Load cogs."""
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')

    async def reload_cogs(self):
        """Load cogs."""
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.reload_extension(f'cogs.{filename[:-3]}')
        return True

    async def setup_hook(self):
        await CONFIG.init_config()
        await self.load_cogs()
        await CONN.open_connection()
        # This copies the global commands over to your guild.
        #self.tree.copy_global_to(guild=MY_GUILD)
        #await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event
async def on_ready():
    """On bot initialized."""
    logging.info('Logged in as %s (ID: %s)', client.user, client.user.id)

client.run(TOKEN, log_handler=None)

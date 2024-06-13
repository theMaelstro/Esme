"""
Main Module
"""
import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

from settings import CONFIG

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
                print(filename)
                await self.load_extension(f'cogs.{filename[:-3]}')

    async def reload_cogs(self):
        """Load cogs."""
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                print(filename)
                await self.reload_extension(f'cogs.{filename[:-3]}')
        return True

    async def setup_hook(self):
        await CONFIG.init_config()
        await self.load_cogs()
        # This copies the global commands over to your guild.
        #self.tree.copy_global_to(guild=MY_GUILD)
        #await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event
async def on_ready():
    """On bot initialized."""
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

client.run(TOKEN)
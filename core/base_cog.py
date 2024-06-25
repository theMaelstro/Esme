import logging

from discord.ext import commands

class BaseCog(commands.Cog):
    """
    Custom base class for Cogs.

    Implements loading and unloading logging.
    """
    async def cog_load(self) -> None:
        logging.info("Cog Loaded: %s.", self.__cog_name__)
        return await super().cog_load()

    async def cog_unload(self) -> None:
        logging.info("Cog Unloaded: %s.", self.__cog_name__)
        return await super().cog_unload()

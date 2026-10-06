"""Cache refresh module."""
import logging
import traceback
import datetime

import requests

from discord.ext import tasks, commands

from sqlalchemy.ext.asyncio import async_sessionmaker
from data.connector import CONN
from data import (
    DiscordBuilder
)

from settings import CONFIG

from core import BaseCog
from core.exceptions import (
    HTTPServerUnreachable
)

URL = "https://api.github.com/repos/theMaelstro/Esme/license"

async def fetch_license(discord_builder: DiscordBuilder):
    """Update Cache variables."""
    logging.info("Fetching license")
    try:
        r = requests.get(
            URL,
            timeout=60
        )
        if r.status_code != 200:
            raise HTTPServerUnreachable(
                "Could not fetch license from repository."
            )

        license_payload = r.json()

        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            # Retrieve guilds.
            json_data = await discord_builder.select_meta(
                session,
                "license"
            )
            if json_data is not None:
                logging.info(
                    "Tested SHA checksums: Source %s against local %s",
                    license_payload['sha'],
                    json_data['sha']
                )
                logging.info("Checksums match: %s", json_data['sha'] == license_payload['sha'])

                if json_data['sha'] != license_payload['sha']:
                    await discord_builder.update_meta(session, "license", license_payload)

            else:
                await discord_builder.insert_meta(session, "license", license_payload)
            # Close Session
            await session.commit()
            await session.close()

        logging.info("Fetching license complete")

    except (
        HTTPServerUnreachable
    ) as e:
        logging.error("Error while fetching License: %s", e)

    except Exception as e:
        logging.error("Error while fetching License: %s %s %s", type(e), e, traceback.format_exc())

class LicenseUpdate(BaseCog):
    """Cog handling updating of License via GitHub api."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.discord_builder = DiscordBuilder()

    async def init_fetch(self):
        """Fetch license during setup."""
        await fetch_license(self.discord_builder)

    @tasks.loop(
        time=datetime.time(hour=12),
        reconnect=True
    )
    async def loop_fetch_license(self):
        """Perform looping fetch at specific hour a day."""
        await fetch_license(self.discord_builder)

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Starting License task: %s.", self.__cog_name__)
        await self.init_fetch()
        self.loop_fetch_license.start()

    async def cog_unload(self) -> None:
        self.loop_fetch_license.cancel()
        logging.info("Stopping License task: %s.", self.__cog_name__)
        return await super().cog_unload()

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(LicenseUpdate(client))

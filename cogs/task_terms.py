"""Cache refresh module."""
import traceback
import logging
import asyncio
import re
import datetime
import json
import hashlib
import hmac

import aiohttp
from aiohttp import web
import requests

import discord
from discord.ext import commands, tasks
from discord import app_commands

from sqlalchemy.ext.asyncio import async_sessionmaker
from data.connector import CONN
from data import (
    DiscordBuilder
)

from settings import CONFIG

from core import BaseCog
from core.exceptions import (
    HTTPServerUnreachable,
    SettingNotConfigured
)

def verify_signature(
    payload_body,
    secret_token,
    signature_header
):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Args:
        payload_body: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    expected_signature = "sha256=" + hmac.new(
        secret_token.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    if hmac.compare_digest(expected_signature, signature_header):
        return True
    return False

async def fetch_terms(discord_builder: DiscordBuilder):
    """Update Cache variables."""
    logging.info("Fetching terms")
    try:
        r = requests.get(
            url=CONFIG.general.terms_of_service,
            timeout=60
        )
        if r.status_code != 200:
            raise HTTPServerUnreachable(
                "Could not fetch terms from repository."
            )

        terms_payload = r.json()

        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            # Retrieve guilds.
            json_data = await discord_builder.select_meta(
                session,
                "terms"
            )
            if json_data is not None:
                logging.info(
                    "Tested SHA checksums: Source %s against local %s",
                    terms_payload['sha'],
                    json_data['sha']
                )
                logging.info("Checksums match: %s", json_data['sha'] == terms_payload['sha'])

                if json_data['sha'] != terms_payload['sha']:
                    await discord_builder.update_meta(session, "terms", terms_payload)

            else:
                await discord_builder.insert_meta(session, "terms", terms_payload)
            # Close Session
            await session.commit()
            await session.close()

        logging.info("Fetching terms complete")
        return True

    except (
        HTTPServerUnreachable
    ) as e:
        logging.error("Error while fetching Terms: %s", e)
        return False

    except Exception as e:
        logging.error("Error while fetching Terms: %s %s %s", type(e), e, traceback.format_exc())
        return False

class TermsUpdate(BaseCog):
    """Cog handling updating of ToS via GitHub api."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.discord_builder = DiscordBuilder()
        self.webhook_server: web.TCPSite = None

    async def init_fetch(self):
        """Fetch terms during setup."""
        return await fetch_terms(self.discord_builder)

    async def webserver(self):
        """Open web server and handle requests."""
        async def handler(request):
            logging.info("Preparing webhook handler")
            try:
                signature_header = request.headers.get("X-Hub-Signature-256")
                logging.info("X-Hub-Signature-256: %s", signature_header)

                if not signature_header:
                    return web.Response(status=403, text="Access Forbidden.")

                body = await request.read()

                if not verify_signature(
                    body,
                    CONFIG.general.terms_webhook_secret,
                    request.headers.get("X-Hub-Signature-256")
                ):
                    return web.Response(status=403, text="Access Forbidden.")

                data = json.loads(body)
                modified = data.get("head_commit", {}).get("modified")
                if not modified:
                    return web.Response(status=500, text="Internal Error.")

                if 'LICENSE' not in modified:
                    return web.Response(status=500, text="Internal Error.")

                await self.init_fetch()

                channel = self.client.get_channel(CONFIG.discord.announcement_channel_id)
                if not channel:
                    raise SettingNotConfigured(
                        "Announcements Channel not configured."
                    )
                embed=discord.Embed(
                        title="Updated Terms of Service",
                        description=(
                            "Our **Terms of Service** have been updated." +
                            "\nPlease use `/terms` command to review the new terms and confirm your agreement." +
                            "\nIf you do not wish to accept them, you can use `/account delete` command to delete data stored via bot interactions."
                        ),
                        color=discord.Color.green()
                    )
                await channel.send(embed=embed)

                return web.Response(status=200, text="OK")

            except json.JSONDecodeError:
                return web.Response(status=400, text="Invalid JSON")
            except aiohttp.ClientError as e:
                logging.warning("aiohttp client error: %s", e)
                return web.Response(
                    status=500,
                    text="Internal error.",
                )
            except aiohttp.http.HttpProcessingError as e:
                logging.warning("aiohttp processing error: %s", e)
                return web.Response(
                    status=500,
                    text="Internal error.",
                )
            except asyncio.TimeoutError as e:
                logging.warning("asyncio timeout error: %s", e)
                return web.Response(
                    status=500,
                    text="Internal error.",
                )

            except (
                SettingNotConfigured
            ) as e:
                logging.warning("Config: %s", e)
                return web.Response(
                    status=500,
                    text="Internal error.",
                )

            except Exception as e:
                logging.error(
                    "Webserver Handler Failed: %s %s %s",
                    type(e),
                    e,
                    traceback.format_exc()
                )
                return web.Response(
                    status=500,
                    text="Internal error",
                )

        app = web.Application()
        app.router.add_post('/esme', handler)

        runner = web.AppRunner(app)
        await runner.setup()

        self.webhook_server = web.TCPSite(
            runner,
            'localhost',
            CONFIG.general.terms_webhook_listen_port
        )

    @tasks.loop(
        time=datetime.time(hour=12),
        reconnect=True
    )
    async def loop_fetch_terms(self):
        """Perform looping fetch at specific hour a day."""
        await fetch_terms(self.discord_builder)

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Starting Terms task: %s.", self.__cog_name__)
        await self.init_fetch()
        await self.client.loop.create_task(self.webserver())
        await self.webhook_server.start()
        await self.loop_fetch_terms.start()

    async def cog_unload(self) -> None:
        await self.loop_fetch_terms.stop()
        await self.webhook_server.stop()
        logging.info("Stopping Terms task: %s.", self.__cog_name__)
        return await super().cog_unload()

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    try:
        if CONFIG.general.terms_of_service is not None:
            if re.match(
                r"^https:\/\/api\.github\.com\/repos\/.*$",
                CONFIG.general.terms_of_service
            ):
                await client.add_cog(TermsUpdate(client))
            else:
                raise SettingNotConfigured(
                    "No valid github api link found for Terms of Service"
                )

    except SettingNotConfigured as e:
        logging.warning(e)

    except Exception as e:
        logging.error("Error while fetching Terms: %s %s %s", type(e), e, traceback.format_exc())

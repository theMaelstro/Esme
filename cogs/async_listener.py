"""Async Listener module with channel handlers for responding to notifiers."""
import asyncio
import logging

import asyncpg_listen
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
import discord
from discord.ext import commands

from data.connector import CONN
from core import BaseCog

class AsyncListener(BaseCog):
    """Cog holding listener and handlers."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.listener_task = None

    async def handle_notifications(
        self,
        notification: asyncpg_listen.NotificationOrTimeout
    ) -> None:
        logging.info("%s has been received", notification)
        if isinstance(notification, asyncpg_listen.listener.Notification):
            logging.info("Notification received: %s", notification)
            embed=discord.Embed(
                    title="New User Appeared",
                    description=(
                        "# Wee Hee Hoo Hoo!\n"
                        f"**Row ID**: `{notification.payload}`"
                    ),
                    color=discord.Color.green()
                )
            embed.set_image(url="https://media1.tenor.com/m/dCKRbYgimZsAAAAd/asby-vtuber.gif")
            channel = self.client.get_channel(1211390842481283145)
            await channel.send(embed=embed)

    async def start_listener(self):
        listener = asyncpg_listen.NotificationListener(
            asyncpg_listen.connect_func(
                host=CONN.url_object.host,
                port=CONN.url_object.port,
                user=CONN.url_object.username,
                password=CONN.url_object.password,
                database=CONN.url_object.database
            )
        )
        listener_task = asyncio.create_task(
            listener.run(
                {"discord_notification": self.handle_notifications},
                policy=asyncpg_listen.ListenPolicy.ALL,
                notification_timeout=-1
            )
        )
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            statements = [
                text("BEGIN;"),
                text("""CREATE OR REPLACE FUNCTION notify_new_discord() RETURNS trigger AS $$
                BEGIN
                PERFORM pg_notify('discord_notification', NEW.id::text);
                RETURN NEW;
                END;"""
                "$$ LANGUAGE plpgsql;"""),
                text("""CREATE OR REPLACE TRIGGER discord_notify_trigger
                AFTER INSERT ON discord
                FOR EACH ROW EXECUTE PROCEDURE notify_new_discord();"""),
                text("COMMIT;")
            ]
            try:
                for statement in statements:
                    await CONN.execute_raw(session, statement)
                logging.info("Discord Table notifier prepared")

            except Exception as e:
                logging.error("Failed to prep notifier: %s", e)

            finally:
                await session.close()

        return listener_task

    async def cog_load(self) -> None:
        try:
            self.listener_task = await self.start_listener()
            logging.info("Listener Started.")

        except Exception as e:
            logging.error("Could not start listener: %s", e)

        return await super().cog_load()

    async def cog_unload(self) -> None:
        try:
            self.listener_task.cancel()
            logging.info("Listener Canceled")

        except Exception as e:
            logging.error("Could not cancel listener: %s", e)

        return await super().cog_unload()

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(AsyncListener(client))

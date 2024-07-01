"""Async Listener module with channel handlers for responding to notifiers."""
import asyncio
import logging
import json
import re

import asyncpg_listen
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
import discord
from discord.ext import commands

from core import BaseCog
from data.connector import CONN
from data import GuildBuilder

class AsyncListener(BaseCog):
    """Cog holding listener and handlers."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.guild_builder = GuildBuilder()
        self.listener_tasks = {}

    async def on_notification_discord(
        self,
        notification: asyncpg_listen.NotificationOrTimeout
    ) -> None:
        """Example handler for notification."""
        logging.info("Received: %s", notification)
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

    async def on_notification_guild_applications(
            self,
            notification: asyncpg_listen.Notification
    ) -> None:
        """
        Handle guild application notification payload
        and send embed results.
        """
        logging.info("Received: %s", notification)
        # Parse payload from json
        payload =json.loads(notification.payload)
        # Start session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            guild_application = await self.guild_builder.select_guild_application_by_id(
                session,
                payload['id']
            )
            discord_ids = await self.guild_builder.select_recruiter_discord_ids(
                session,
                payload['guild_id']
            )
            await session.close()

        # Prepare embed
        embed=discord.Embed(
            title="New Guild Application Pending",
            description=(
                f"# {re.escape(guild_application.guild_name)}\n"
            ),
            color=discord.Color.blue()
        )
        embed.add_field(
            name=f"{payload['application_type'].title()} to Guild",
            value=re.escape(guild_application.initiate_name),
            inline=False
        )
        embed.add_field(
            name="Issued At",
            value=f"<t:{round(guild_application.applied_on)}:f>",
            inline=False
        )
        # Add management fields if application is received.
        if payload['application_type'] == 'applied':
            if discord_ids:
                embed.add_field(
                    name="Guild Recruiters",
                    value=f"{''.join(f'<@{str(i)}>' for i in discord_ids)}",
                    inline=False
                )
            embed.add_field(
                name="Accept",
                value=f"```application id:{payload['id']} accept```",
                inline=False
            )
            embed.add_field(
                name="Decline",
                value=f"```application id:{payload['id']} decline```",
                inline=False
            )
        embed.set_footer(
            text=f"Requested by {re.escape(guild_application.progenitor_name)}"
        )

        # TODO: Add guild application channel to config.
        channel = self.client.get_channel(1211390842481283145)
        await channel.send(embed=embed)

    async def start_listeners(self) -> dict:
        """Prepare and start listener tasks."""
        # Start session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            # Prepare notifier creation queries.
            statements = [
                text("BEGIN;"),

                # Discord
                text("""CREATE OR REPLACE FUNCTION notify_new_discord() RETURNS trigger AS $$
                BEGIN
                PERFORM pg_notify('discord_notification', NEW.id::text);
                RETURN NEW;
                END;"""
                "$$ LANGUAGE plpgsql;"""),
                text("""CREATE OR REPLACE TRIGGER discord_notify_trigger
                AFTER INSERT ON discord
                FOR EACH ROW EXECUTE PROCEDURE notify_new_discord();"""),

                # Guild Application
                text("""CREATE OR REPLACE FUNCTION notify_new_guild_application() RETURNS trigger AS $$
                BEGIN
                PERFORM pg_notify('guild_application_notification', row_to_json(NEW)::text);
                RETURN NEW;
                END;"""
                "$$ LANGUAGE plpgsql;"""),
                text("""CREATE OR REPLACE TRIGGER guild_application_notify_trigger
                AFTER INSERT ON guild_applications
                FOR EACH ROW EXECUTE PROCEDURE notify_new_guild_application();"""),

                text("COMMIT;")
            ]
            try:
                for statement in statements:
                    await CONN.execute_raw(session, statement)
                logging.info("Notifiers prepared")

            except Exception as e:
                logging.error("Failed to prep notifiers: %s", e)

            finally:
                await session.close()

            # Create listener connection
            listener = asyncpg_listen.NotificationListener(
                asyncpg_listen.connect_func(
                    host=CONN.url_object.host,
                    port=CONN.url_object.port,
                    user=CONN.url_object.username,
                    password=CONN.url_object.password,
                    database=CONN.url_object.database
                )
            )

            # Prepare listener tasks and return dict.
            return {
                "discord": asyncio.create_task(
                    listener.run(
                        {"discord_notification": self.on_notification_discord},
                        policy=asyncpg_listen.ListenPolicy.ALL,
                        notification_timeout=-1
                    )
                ),
                "guild_application": asyncio.create_task(
                    listener.run(
                        {"guild_application_notification": self.on_notification_guild_applications},
                        policy=asyncpg_listen.ListenPolicy.ALL,
                        notification_timeout=-1
                    )
                )
            }

    async def cog_load(self) -> None:
        try:
            # Start listeren tasks.
            self.listener_tasks = await self.start_listeners()
            logging.info("Listener Started.")

        except Exception as e:
            logging.error("Could not start listener: %s", e)

        return await super().cog_load()

    async def cog_unload(self) -> None:
        try:
            # Gracefully cancel listener tasks
            for key, task in self.listener_tasks.items():
                task.cancel()
                logging.info("Listener Canceled Succesfuly: %s", key)

        except Exception as e:
            logging.error("Could not cancel listener: %s", e)

        return await super().cog_unload()

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(AsyncListener(client))

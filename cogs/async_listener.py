"""Async Listener module with channel handlers for responding to notifiers."""
import asyncio
from datetime import datetime, UTC, timedelta
import logging
import json
import re

import asyncpg_listen
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
import discord
from discord.ext import commands

from core import BaseCog
from core.exceptions import CoroutineFailed
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
        # Type of Application
        embed.add_field(
            name=f"{payload['application_type'].title()} to Guild",
            value=re.escape(guild_application.initiate_name),
            inline=False
        )
        # Time of creation
        embed.add_field(
            name="Issued At",
            value=f"<t:{round(guild_application.applied_on)}:f>",
            inline=False
        )
        # Add management fields if application is received.
        if payload['application_type'] == 'applied':
            if discord_ids:
                # Users responsible for action
                embed.add_field(
                    name="Guild Recruiters",
                    value=f"{''.join(f'<@{str(i)}>' for i in discord_ids)}",
                    inline=False
                )
            # Actions
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
        # Application Creator
        embed.set_footer(
            text=f"Requested by {re.escape(guild_application.creator_name)}"
        )

        # TODO: Add guild application channel to config.
        # TODO: Add check for guild channel id, if empty raise exception
        channel = self.client.get_channel(1211390842481283145)
        await channel.send(embed=embed)

    async def on_notification_events(
            self,
            notification: asyncpg_listen.Notification
    ) -> None:
        """
        Handle events notification payload,
        create Discord related Events
        and send embed response to log channel.
        """
        logging.info("Received: %s", notification)
        # Parse payload from json
        payload =json.loads(notification.payload)
        if payload['event_type'] == 'festa':
            utc_time_now = datetime.now(UTC) + timedelta(seconds=10)
            # TODO: Add guild to config
            guild = self.client.get_guild(1211390841705332806)
            channel = self.client.get_channel(1211390842481283145)
            try:
                events = {
                    "Festi Registration Week": await guild.create_scheduled_event(
                        name = f"Hunter Festival #{payload['id']}: Registration",
                        start_time = utc_time_now,
                        entity_type=discord.EntityType.external,
                        privacy_level=discord.PrivacyLevel.guild_only,
                        location="Renewal Game Server",
                        end_time= utc_time_now + timedelta(days=7),
                        description=(
                            "*Festival Registration week just started."
                            "Guild leaders can now sign-up their Guilds for participation."
                            "Registered Guild will be randomly assigned team color.*"
                        ),
                        reason="Festa Trials in game began."
                    ),
                    "Festi Hunting Week": await guild.create_scheduled_event(
                        name = f"Hunter Festival #{payload['id']}: Hunting",
                        start_time = utc_time_now + timedelta(days=7),
                        entity_type=discord.EntityType.external,
                        privacy_level=discord.PrivacyLevel.guild_only,
                        location="Renewal Game Server",
                        end_time= utc_time_now + timedelta(days=14),
                        description=(
                            "*Festival Hunting week just started."
                            "Take part in game activities to earn Soul Points for your team."
                            "Remember to donate your gained points."
                            "Lead your team to victory to gain access to unique rewards!*\n"

                            "## Secret Quests Schedule\n"
                            "1. <t:1718618400:t> - <t:1718625600:t>\n"
                            "2. <t:1718647200:t> - <t:1718654400:t>\n"
                            "3. <t:1718589600:t> - <t:1718596800:t>\n"

                            "## Rules\n"
                            "- 3 time windows per day, each lasting 2 hours\n"
                            "- during each 6 secret quests will be available,"
                            "awarding additional points to the losing team\n"
                            "- 2 quests per each of **HR5**, **HR6**, **G** ranks"
                        ),
                        reason="Festa Trials in game began."
                    ),
                    "Festi Rewards Week": await guild.create_scheduled_event(
                        name = f"Hunter Festival #{payload['id']}: Rewards",
                        start_time = utc_time_now + timedelta(days=14),
                        entity_type=discord.EntityType.external,
                        privacy_level=discord.PrivacyLevel.guild_only,
                        location="Renewal Game Server",
                        end_time= utc_time_now + timedelta(days=21),
                        description="Event DESC",
                        reason="Festa Trials in game began."
                    ),
                }
                for key, event in events.items():
                    if event:
                        logging.info("Created Event: %s", event.name)
                        await channel.send(
                            embed=discord.Embed(
                                title=event.name,
                                description=(
                                    "# Created Event\n"
                                    f"Start: {discord.utils.format_dt(event.start_time, 'f')}\n"
                                    f"End: {discord.utils.format_dt(event.end_time, 'f')}"
                                ),
                                color=discord.Color.green()
                            )
                        )
                    else:
                        raise CoroutineFailed(
                            f"Could not create Event: {key}"
                        )

            except (
                CoroutineFailed
            ) as e:
                logging.error("Hunter Festival: %s", e)

            except (
                Exception
            ) as e:
                logging.error("Unhandled exception: %s", e)

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

                # Event
                text("""CREATE OR REPLACE FUNCTION notify_new_events() RETURNS trigger AS $$
                BEGIN
                PERFORM pg_notify('events_notification', row_to_json(NEW)::text);
                RETURN NEW;
                END;"""
                "$$ LANGUAGE plpgsql;"""),
                text("""CREATE OR REPLACE TRIGGER events_notify_trigger
                AFTER INSERT ON events
                FOR EACH ROW EXECUTE PROCEDURE notify_new_events();"""),

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
                ),
                "event": asyncio.create_task(
                    listener.run(
                        {"events_notification": self.on_notification_events},
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

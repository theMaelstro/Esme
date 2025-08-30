"""Extension module for GuildList Cog."""
import logging
import asyncio
import re
from typing import Literal
from http.client import responses
import aiohttp
from aiohttp import web

import discord
from discord.ext import commands, tasks
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from core import BaseCog
from core.exceptions import (
    SettingNotConfigured
)

from data.connector import CONN
from data import UniversalBuilder

from settings import CONFIG

class LiveChatTask(BaseCog):
    """Cog handling live chat server."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.guild: discord.Guild
        self.universal_builder = UniversalBuilder()
        self.chat_server: web.TCPSite = None
        self.chat_client: aiohttp.ClientSession = None
        self.channels: list[discord.TextChannel] = None
        self.servers = None
        self.received_message_pool: list[dict] = []
        self.queued_message_pool: list[dict] = []

    async def webserver(self):
        """Open web server and handle requests."""
        async def handler(request):
            try:
                data = await request.json()
                logging.info("Received request: %s.", data['player'])
                if data['api_key'] != CONFIG.livechat.api_key:
                    logging.info("Received request with invalid api key.")
                    return web.Response(status=401, text="Unauthorized")
                self.received_message_pool.append(
                    {
                    "channel": data['channel'],
                    "player": re.sub(r'[^A-Za-z0-9 ]+', '', data['player']),
                    "content": re.sub(r'[^A-Za-z0-9 ]+', '', data['content'])
                    })
                return web.Response(status=200, text="OK")
                #raise web.HTTPInternalServerError(text='JSONError')
            except aiohttp.ClientError as e:
                logging.info("aiohttp client error: %s", e)
            except aiohttp.http.HttpProcessingError as e:
                logging.info("aiohttp processing error: %s", e)
            except asyncio.TimeoutError as e:
                logging.info("asyncio timeout error: %s", e)
            except Exception as e:
                logging.info("generic error: %s", e)

        app = web.Application()
        app.router.add_post('/chat/', handler)
        runner = web.AppRunner(app)
        await runner.setup()
        self.chat_server = web.TCPSite(runner, 'localhost', CONFIG.livechat.listen_port)

    async def webclient(self, channel_id: int, player: str, content: str, msg_type: str):
        """Open web client session and send request."""
        self.chat_client = aiohttp.ClientSession(timeout = aiohttp.ClientTimeout(total=10))
        try:
            async with self.chat_client.post(
                f"http://localhost:{CONFIG.livechat.remote_port}/chat/{channel_id}/",
                json={
                    "api_key": CONFIG.livechat.api_key,
                    "type": msg_type,
                    "player": player,
                    "content": content,
                },
                headers = {"Content-Type": "application/json; charset=UTF-8"}
            ) as response:
                await self.chat_client.close()
                return response.status
        except aiohttp.ClientConnectorError as e:
            logging.info("aiohttp connection error: %s", e)
            await self.chat_client.close()
            return False
        except aiohttp.ClientError as e:
            logging.info("aiohttp client error: %s", e)
            await self.chat_client.close()
            return web.Response(status=400, text="Bad Request")
        except aiohttp.http.HttpProcessingError as e:
            logging.info("aiohttp processing error: %s", e)
            await self.chat_client.close()
            return web.Response(status=400, text="Bad Request")
        except asyncio.TimeoutError as e:
            logging.info("asyncio timeout error: %s", e)
            await self.chat_client.close()
            return web.Response(status=408, text="Request Timeout")
        except Exception as e:
            logging.info("generic error: %s", e)
            await self.chat_client.close()
            return False

    def get_server_name_by_id(self, channel_id):
        for server in self.servers:
            if str(server.server_id) == channel_id:
                return f"{server.world_name.lower()}-{server.land}".replace(" ", "-")
        return None

    def get_server_id_by_name(self, channel_name):
        for server in self.servers:
            if f"{server.world_name.lower()}-{server.land}".replace(" ", "-") == channel_name:
                return server.server_id
        return None

    async def receive_message(self, channel_id: str, player: str, content: str):
        """Receive message from server and send it to discord channel."""
        for channel in self.channels:
            if channel.name == self.get_server_name_by_id(channel_id):
                await channel.send(f"**{player}**: {content}")
                return True
        return False

    async def send_message(self):
        """Send queued message to server."""
        logging.info("Queued Messages: %s.", len(self.queued_message_pool))
        bottom_stack = self.queued_message_pool.pop(0)
        message: discord.Message = bottom_stack['message']
        if (
            response := await self.webclient(
                bottom_stack['channel'],
                bottom_stack['player'],
                bottom_stack['content'],
                "normal"
            )
        ) != web.HTTPOk.status_code:
            await message.channel.send(
                embed=discord.Embed(
                    title="Warning",
                    description=(
                            "Server did not respond.\n"
                            f"```{bottom_stack['content']}```"
                        ),
                    color=discord.Color.red()
                ).set_author(name=message.author, icon_url=message.author.display_avatar)
            )
            logging.info(
                "Message not sent, server does not respond: %s", responses.get(response)
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id != self.client.user.id:
            if message.channel in self.channels:
                channel_id = self.get_server_id_by_name(message.channel.name)
                logging.info("Received Message: %s.", message.content)
                player = f"{re.sub(r'[^A-Za-z0-9 ]+', '', message.author.display_name)}"
                mentioned_user = re.compile(r'<@\d{16,20}>')
                emoji = re.compile(r'<:\w+:\d{16,20}>')
                content = message.content

                # User mentions
                while (mu := mentioned_user.search(content)) is not None:
                    raw_mention = mu.group()
                    user_id = re.sub("[^0-9]", "", raw_mention)
                    user_mention: discord.User = message.guild.get_member(int(user_id))
                    if user_mention is not None:
                        content = content.replace(raw_mention, user_mention.display_name)
                    else:
                        content = content.replace(raw_mention, "mentioned")

                # Emojis
                while (me := emoji.search(content)) is not None:
                    raw_mention = me.group()
                    content = content.replace(raw_mention, raw_mention.split(":")[1])

                content = " ".join(
                    f"{re.sub(
                        r'[^A-Za-z0-9 ]+',
                        '',
                        content
                    )}".split()
                )

                if player.strip(" ") == "" or content.strip(" ") == "":
                    await message.channel.send(
                        embed=discord.Embed(
                            title="Warning",
                            description= (
                                "Message was not sent.\n"
                                "Check if your server name or message content is"
                                " not made up of just special characters."
                            ),
                            color=discord.Color.red()
                        ).set_author(name=message.author, icon_url=message.author.display_avatar)
                    )
                    return
                if len(content) > 92:
                    content = content[:92]
                    await message.channel.send(
                        embed=discord.Embed(
                            title="Warning",
                            description= (
                                "Parsed message is too long.\n"
                                "Slice will be used.\n"
                                f"```{content}```"
                            ),
                            color=discord.Color.blue()
                        ).set_author(name=message.author, icon_url=message.author.display_avatar)
                    )

                self.queued_message_pool.append(
                {
                    "channel": channel_id,
                    "player": player,
                    "content": content,
                    "message": message
                })

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Retrieving Guild: %s.", self.__cog_name__)
        self.guild = self.client.get_guild(CONFIG.discord.guild_id)
        if not self.guild:
            raise SettingNotConfigured(
                "Logs channel not configured."
            )

        # Create session
        async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
        async with async_session() as session:
            # Retrieve servers.
            self.servers = await self.universal_builder.get_players_online_per_land(session)

            # Close Session
            await session.commit()
            await session.close()

        category = discord.utils.get(
            self.guild.categories,
            id=CONFIG.discord.live_chat_category_id
        )
        if not category:
            raise SettingNotConfigured(
                "Logs channel not configured."
            )
        channels = [channel.name for channel in category.channels]
        for i, server in enumerate(self.servers):
            channel_name = f"{server.world_name.lower()}-{server.land}".replace(" ", "-")
            if not channel_name in channels:
                logging.info(
                    "Creating Missing Channel: %s, %s",
                    channel_name,
                    self.__cog_name__
                )
                try:
                    await self.guild.create_text_channel(
                        name=channel_name,
                        category=category,
                        position=i
                    )
                except (
                    discord.Forbidden,
                    discord.HTTPException,
                    TypeError
                ) as e:
                    logging.error("%s: %s.", e, self.__cog_name__)
        self.channels = category.channels

        logging.info("Starting Status task: %s.", self.__cog_name__)
        await self.client.loop.create_task(self.webserver())
        await self.chat_server.start()
        await self.empty_pool.start()

    @tasks.loop(seconds=0.2)
    async def empty_pool(self):
        """Empty message pools."""
        if len(self.received_message_pool) > 0:
            logging.info("Received Messages: %s.", len(self.received_message_pool))
            bottom_stack = self.received_message_pool.pop(0)
            await self.receive_message(
                bottom_stack['channel'],
                bottom_stack['player'],
                bottom_stack['content']
            )

        if len(self.queued_message_pool) > 0:
            if self.chat_client is not None:
                if self.chat_client.closed:
                    await self.send_message()
            else:
                await self.send_message()

    @app_commands.command(
        name="broadcast",
        description="Broadcast message across all in-game channels."
    )
    async def broadcast(
        self,
        interaction: discord.Interaction,
        msg_type: Literal["admin", "system"],
        content: str
    ):
        """Broadcast message across all in-game channels."""
        player = f"{re.sub(r'[^A-Za-z0-9 ]+', '', interaction.user.display_name)}"
        content_sane = f"{re.sub(r'[^A-Za-z0-9 ]+', '', content)}"

        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            embed=discord.Embed(
                title="Broadcast",
                description="Process started. Sending messages.",
                color=discord.Color.blue()
            ),
            ephemeral=True
        )

        broadcast_result = []
        for server in self.servers:
            response = await self.webclient(
                server.server_id,
                player,
                content_sane,
                msg_type
            )
            if response is False:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Broadcast Failed",
                        description="Server did not respond.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                logging.info(
                    "%s: %s",
                    interaction.user.id,
                    "Broadcast not sent, server does not respond."
                )
                return

            broadcast_result.append(
                f"Channel {server.server_id}: `{responses.get(response)}`"
            )
            logging.info("Channel %s: %s", server.server_id, responses.get(response))

        await interaction.followup.send(
            embed=discord.Embed(
                title="Broadcast",
                description=(
                    "## Process finished:\n"
                    + "\n".join(broadcast_result)
                ),
                color=discord.Color.green()
            ),
            ephemeral=True
        )
        logging.info("%s: %s", interaction.user.id, "Sent broadcast.")

    async def cog_unload(self) -> None:
        await self.chat_server.stop()
        logging.info("Stopping Status task: %s.", self.__cog_name__)
        return await super().cog_unload()

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.features.tasks.live_chat.enabled:
        await client.add_cog(LiveChatTask(client))

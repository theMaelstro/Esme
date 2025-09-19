"""Extension module for GuildList Cog."""
import logging
from random import randrange

import discord
from discord.ext import commands
from discord import app_commands
from sqlalchemy.ext.asyncio import async_sessionmaker

from data.connector import CONN
from data import (
    CharactersBuilder,
    DiscordBuilder
)

from settings import CONFIG
from core import BaseCog
from core.exceptions import (
    CharacterNotSet,
    CoroutineFailed,
    DiscordNotRegistered,
    MissingPermissions
)

from core.binary_handler import (
    compress,
    decompress,
    CharacterData
)

def loop_bit_group(group, count, check):
    if count != 0:
        if check is True:
            group += "1"
        else:
            group += "0"
        for _ in range(count):
            group += "1"
    return group

def leading_zero_hex(group):
    if len(group) < 2:
        i = len(group)
        while i < 2:
            group += "0"
        group = group.split("").reverse().join("")
        i += 1
    return group

def calculate_flag(
    count_hr1: bool,
    count_hr2: bool,
    count_hr3: bool,
    count_hr4: bool,
    count_hr5: bool,
    count_hr6: bool,
    urgent_hr1: bool,
    urgent_hr2: bool,
    urgent_hr3: bool,
    urgent_hr4: bool,
    urgent_hr5: bool,
    urgent_hr6: bool
) -> str:
    sign = "0"
    bitgroup = ""
    if count_hr1 != 0:
        bitgroup = sign + loop_bit_group(bitgroup, count_hr1, urgent_hr1)
        bitgroup = loop_bit_group(bitgroup, count_hr2, urgent_hr2)
        bitgroup = loop_bit_group(bitgroup, count_hr3, urgent_hr3)
        bitgroup = loop_bit_group(bitgroup, count_hr4, urgent_hr4)
        bitgroup = loop_bit_group(bitgroup, count_hr5, urgent_hr5)
        bitgroup = loop_bit_group(bitgroup, count_hr6, urgent_hr6)

        i = len(bitgroup)
        while i < 64:
            bitgroup += "0"
            i += 1

        i = 0
        my_bit = ""
        while i < 64:
            my_bit += hex(int(bitgroup[i:i+8][::-1], 2))[2:].zfill(2)
            i += 8

    return my_bit

class KeyFlag(BaseCog):
    """Cog handling calculation of key flag."""
    def __init__(self, client: commands.Bot):
        self.client = client
        self.character_builder = CharactersBuilder()
        self.discord_builder = DiscordBuilder()

    group_keyflag = app_commands.Group(
        name="keyflag",
        description="..."
    )

    @group_keyflag.command(
        name="get",
        description="Calculate keyquest flag."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.keyflag.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    @app_commands.describe(hr1="Number of quests you finished on HR1.")
    @app_commands.describe(hr2="Number of quests you finished on HR2.")
    @app_commands.describe(hr3="Number of quests you finished on HR3.")
    @app_commands.describe(hr4="Number of quests you finished on HR4.")
    @app_commands.describe(hr5="Number of quests you finished on HR5.")
    @app_commands.describe(hr6="Number of quests you finished on HR6.")
    @app_commands.describe(u1="Did you finish Urgent quest after HR1?")
    @app_commands.describe(u2="Did you finish Urgent quest after HR2?")
    @app_commands.describe(u3="Did you finish Urgent quest after HR3?")
    @app_commands.describe(u4="Did you finish Urgent quest after HR4?")
    @app_commands.describe(u5="Did you finish Urgent quest after HR5?")
    @app_commands.describe(u6="Did you finish Urgent quest after HR6?")

    async def keyflag_get(
        self,
        interaction: discord.Interaction,
        hr1: app_commands.Range[int, 0, 30],
        u1: bool,
        hr2: app_commands.Range[int, 0, 30],
        u2: bool,
        hr3: app_commands.Range[int, 0, 30],
        u3: bool,
        hr4: app_commands.Range[int, 0, 30],
        u4: bool,
        hr5: app_commands.Range[int, 0, 30],
        u5: bool,
        hr6: app_commands.Range[int, 0, 30],
        u6: bool
    ):
        """Calculate flag."""
        try:
            if not CONFIG.check_permission(
                CONFIG.commands.keyflag.permission,
                interaction.user
            ):
                raise MissingPermissions(
                    f"{interaction.user.mention} is missing permissions to use command."
                )
            flag = calculate_flag(
                hr1,
                hr2,
                hr3,
                hr4,
                hr5,
                hr6,
                u1,
                u2,
                u3,
                u4,
                u5,
                u6
            )
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Keyflag",
                    description=(
                        "# Flag Details\n"
                        "       Quests    Urgents\n"
                        f"HR1:  `{hr1}`  `{u1}`\n"
                        f"HR2:  `{hr2}`  `{u2}`\n"
                        f"HR3:  `{hr3}`  `{u3}`\n"
                        f"HR4:  `{hr4}`  `{u4}`\n"
                        f"HR5:  `{hr5}`  `{u5}`\n"
                        f"HR6:  `{hr6}`  `{u6}`\n"
                        "# Result\n"
                        f"```!kqf set {flag}```"
                    ),
                    color=discord.Color.green()
                ),
                ephemeral=True
            )
        except (
            MissingPermissions
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Keyflag Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @group_keyflag.command(
        name="set",
        description="Exit game before use. Calculate keyquest flag and update your save."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.keyflag.cooldown,
        key=lambda i: (i.guild_id, i.user.id)
    )
    @app_commands.describe(hr1="Number of quests you finished on HR1.")
    @app_commands.describe(hr2="Number of quests you finished on HR2.")
    @app_commands.describe(hr3="Number of quests you finished on HR3.")
    @app_commands.describe(hr4="Number of quests you finished on HR4.")
    @app_commands.describe(hr5="Number of quests you finished on HR5.")
    @app_commands.describe(hr6="Number of quests you finished on HR6.")
    @app_commands.describe(u1="Did you finish Urgent quest after HR1?")
    @app_commands.describe(u2="Did you finish Urgent quest after HR2?")
    @app_commands.describe(u3="Did you finish Urgent quest after HR3?")
    @app_commands.describe(u4="Did you finish Urgent quest after HR4?")
    @app_commands.describe(u5="Did you finish Urgent quest after HR5?")
    @app_commands.describe(u6="Did you finish Urgent quest after HR6?")

    async def keyflag_set(
        self,
        interaction: discord.Interaction,
        hr1: app_commands.Range[int, 0, 30],
        u1: bool,
        hr2: app_commands.Range[int, 0, 30],
        u2: bool,
        hr3: app_commands.Range[int, 0, 30],
        u3: bool,
        hr4: app_commands.Range[int, 0, 30],
        u4: bool,
        hr5: app_commands.Range[int, 0, 30],
        u5: bool,
        hr6: app_commands.Range[int, 0, 30],
        u6: bool
    ):
        """Calculate flag."""
        try:
            if not CONFIG.check_permission(
                CONFIG.commands.keyflag.permission,
                interaction.user
            ):
                raise MissingPermissions(
                    f"{interaction.user.mention} is missing permissions to use command."
                )

            # Create session
            async_session = async_sessionmaker(CONN.engine, expire_on_commit=False)
            async with async_session() as session:
                # Check if user is registered.
                discord_user = await self.discord_builder.select_discord_user(
                    session,
                    str(interaction.user.id)
                )

                if discord_user is None:
                    raise DiscordNotRegistered(
                        "No account registered for this discord user."
                    )

                # Get character list.
                character = await self.character_builder.select_character_details_by_character_id(
                    session,
                    discord_user.character_id
                )
                if character is None:
                    raise CharacterNotSet(
                        "No character selected. Please use `/account character select` command."
                    )

                data = await self.character_builder.get_character_save(
                    session,
                    discord_user.character_id
                )
                flag = calculate_flag(
                    hr1, hr2, hr3, hr4, hr5, hr6,
                    u1, u2, u3, u4, u5, u6
                )

                character = CharacterData(decompress(data.savedata.file_data))
                character.set_keyflag(flag)
                c = compress(character.save_data)

                if not await self.character_builder.update_character_save(
                    session,
                    discord_user.character_id,
                    c
                ):
                    raise CoroutineFailed(
                        "Could not update character save."
                    )

                # Close Session
                await session.commit()
                await session.close()

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Flag Set",
                    description=(
                        f"Flag: `{flag}` has been applied to your save file.\n"
                        "Swap land or relog to see changes."
                    ),
                    color=discord.Color.green()
                ),
                ephemeral=True
            )
        except (
            CoroutineFailed,
            CharacterNotSet,
            DiscordNotRegistered,
            MissingPermissions
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Keyflag Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @keyflag_set.error
    async def on_keyflag_set_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.keyflag.enabled:
        await client.add_cog(KeyFlag(client))

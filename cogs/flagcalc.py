"""Extension module for GuildList Cog."""
import discord
from discord.ext import commands
from discord import app_commands

from settings import CONFIG
from core import BaseCog

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
    count_hr1,
    count_hr2,
    count_hr3,
    count_hr4,
    count_hr5,
    count_hr6,
    urgent_hr1,
    urgent_hr2,
    urgent_hr3,
    urgent_hr4,
    urgent_hr5,
    urgent_hr6
):
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

    @app_commands.command(
        name="keyflag",
        description="Calculate keyquest flag."
    )
    @app_commands.checks.cooldown(
        1,
        CONFIG.commands.guild_list.cooldown,
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
    async def flag_calc(
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
        """Show all guilds."""
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

    @flag_calc.error
    async def on_flag_calc_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """On cooldown send remaining time info message."""
        await self.on_cooldown_response(interaction, error)

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    if CONFIG.commands.guild_list.enabled:
        await client.add_cog(KeyFlag(client))

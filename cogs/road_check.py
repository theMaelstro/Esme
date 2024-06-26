"""Extension module for Road Cog."""

import codecs
import logging

import requests
import discord
from discord.ext import commands
from discord import app_commands

from settings import CONFIG
from core import BaseCog
from core import MissingPermissions

class Road(BaseCog):
    """Cog handling reading road progress data."""
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(
        name="checkroadstats",
        description="Checks the road stats of the given file."
    )
    async def check_road_stats(
        self, interaction: discord.Interaction,
        file: discord.Attachment
    ):
        """Check rengoku save file."""
        try:
            if interaction.user.id not in CONFIG.discord.admin_user_ids:
                raise MissingPermissions(
                    f"{interaction.user.mention} is missing permissions."
                )

            # save the file to a location in an accessible directory.
            await self.writefile(file)

            # obtain data from previously saved file.
            hex_main = await self.readfile(file)

            # read the values from the previously obtained data.
            mainv = await self.readvalues(hex_main)

            # initialize the embed.
            embed = discord.Embed(
                title=f"Results for {hash(file.url)}.bin",
                color=discord.Color.green()
            )
            # add field for floors.
            embed.add_field(
                name="Reached Floor",
                value=f"{mainv[1]:,}",
                inline=False
            )

            # add field for points.
            embed.add_field(
                name="Earned Points",
                value=f"{mainv[2]:,}",
                inline=False
            )

            # sends the data back to the user.
            logging.info("%s: %s", interaction.user.id, embed.title)
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

        except (
            MissingPermissions
        ) as e:
            logging.warning("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Road Check Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        except (
            ValueError
        ) as e:
            logging.error("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Road Check Failed",
                    description=e,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        except (
            Exception
        ) as e:
            logging.error("%s: %s", interaction.user.id, e)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Road Check Failed",
                    description=(
                        "Uhandled Exception.\n"
                        "Contact bot admin."
                    ),
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    # reads a file and turns it into a hexdump.
    async def readfile(self, file):
        """Reads binary file from folder."""
        # MAKE SURE THE FOLDER EXISTS.
        with open(f"test/{hash(file.url)}.bin", 'rb') as f:
            for chunk in iter(lambda: f.read(), b''):
                hex_dump = codecs.encode(chunk, 'hex')
        return hex_dump

    # writes a new file with obtained data.
    async def writefile(self, file):
        """Requests remote file and saves it."""
        r = requests.get(
            file.url,
            allow_redirects=True,
            timeout=120
        )

        # MAKE SURE THE FOLDER EXISTS.
        with open(
            f"test/{hash(file.url)}.bin",
            "wb"
        ) as f: f.write(r.content)
        logging.info('Written new data to test/%s.bin.', hash(file.url))

    # gets necessary values to get the pointers and stuff.
    async def readvalues(self, source_bytes):
        """Read values."""
        # make sure it's the same filelength to minimize risk of it not being rengokudata.bin
        file_length = int(len(source_bytes)/2)
        if file_length != 95:
            raise ValueError(
                (
                    "This file is not of the appropriate type.\n"
                    f"Expected length: 95. | Current length:{file_length}."
                )
            )

        # bytes where the max floor is stored.
        hex_mfr = source_bytes[146:150].decode()
        hex_mpr = source_bytes[150:158].decode()

        # value for max floors reached turned into an integer so "normal" "humans" can read it.
        max_floor_reached = int(f'0x{hex_mfr}', 0)
        # value for max points reached turned into an integer.
        max_points_reached = int(f'0x{hex_mpr}', 0)

        return [file_length, max_floor_reached, max_points_reached]

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(Road(client))

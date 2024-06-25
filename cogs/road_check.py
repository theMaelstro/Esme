import codecs
import logging

import requests
import discord
from discord.ext import commands
from discord import app_commands

from settings import CONFIG
from core import BaseCog

class Road(BaseCog):
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
        if interaction.user.id in CONFIG.discord.admin_user_ids:
            # initialize the embed.
            embed = discord.Embed(
                title=f"Results for {hash(file.url)}.bin:",
                color=0x00ff00
            )
            try: # catch errors
                # save the file to a location in an accessible directory.
                await self.writefile(file)

                # obtain data from previously saved file.
                hex_main = await self.readfile(file)

                # read the values from the previously obtained data.
                mainv = await self.readvalues(hex_main)

                # add field for floors.
                embed.add_field(name="Highest floor reached:", value=f"{mainv[1]:,}")

                # add field for points.
                embed.add_field(name="Highest points earned:", value=f"{mainv[2]:,}")

            # logs the error.
            except Exception as e:
                # user gets informed of an incorrect file being uploaded.
                embed.add_field(
                    name="Error",
                    value=f"Error: {e}"
                )
            # sends the data back to the user.
            await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            await interaction.response.send_message(
                f"You are not allowed to use this command {interaction.user.mention}.",
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
    async def readvalues(self, bytes):
        """Read values."""
        # make sure it's the same filelength to minimize risk of it not being rengokudata.bin
        file_length = int(len(bytes)/2)
        if file_length != 95:
            raise ValueError(
                (
                    "This file is not of the appropriate type.\n"
                    f"Expected length: 95. | Current length:{file_length}."
                )
            )

        # bytes where the max floor is stored.
        hex_mfr = bytes[146:150].decode()
        hex_mpr = bytes[150:158].decode()

        # value for max floors reached turned into an integer so "normal" "humans" can read it.
        max_floor_reached = int(f'0x{hex_mfr}', 0)
        # value for max points reached turned into an integer.
        max_points_reached = int(f'0x{hex_mpr}', 0)

        return [file_length, max_floor_reached, max_points_reached]

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(Road(client))

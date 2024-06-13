import requests
import codecs
import discord
from discord.ext import commands
from discord import app_commands
from settings import CONFIG

class Road(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="checkroadstats", description="Checks the road stats of the given file.")
    async def checkroadstats(self, interaction: discord.Interaction, file: discord.Attachment):
        embed = discord.Embed(title=f"Results for {hash(file.url)}.bin:", color=0x00ff00) # initialize the embed.
        try: # catch errors
            await Road.writefile(file) # save the file to a location in an accessible directory.
            hex_main = await Road.readfile(file) # obtain data from previously saved file.
            mainv = await Road.readvalues(hex_main) # read the values from the previously obtained data.
            embed.add_field(name="Highest floor reached:", value=f"{mainv[1]:,}") # add field for floors.
            embed.add_field(name="Highest points earned:", value=f"{mainv[2]:,}") # add field for points.
        except Exception as e: # logs the error.
            embed.add_field(name="Error", value=f"Error: {e}") # user gets informed of an incorrect file being uploaded.
        await interaction.response.send_message(embed=embed) # sends the data back to the user.

    async def readfile(file): # reads a file and turns it into a hexdump.
        with open(f"test/{hash(file.url)}.bin", 'rb') as f: # MAKE SURE THE FOLDER EXISTS.
            for chunk in iter(lambda: f.read(), b''):
                hex_dump = codecs.encode(chunk, 'hex')
        return hex_dump

    async def writefile(file): # writes a new file with obtained data.
        r = requests.get(file.url, allow_redirects=True)
        with open(f"test/{hash(file.url)}.bin", "wb") as f: f.write(r.content) # MAKE SURE THE FOLDER EXISTS.
        print(f'Written new data to test/{hash(file.url)}.bin .')

    async def readvalues(bytes): # gets necessary values to get the pointers and stuff.
        fileLength = int(len(bytes)/2) # make sure it's the same filelength to minimize risk of it not being rengokudata.bin
        if fileLength != 95: raise ValueError(f"This file is not of the appropriate type.\nExpected length: 95. | Current length:{fileLength}.") 
        hexMFR = bytes[146:150].decode()        # bytes where the max floor is stored.
        hexMPR = bytes[150:158].decode()
        maxFloorReached = int(f'0x{hexMFR}', 0) # value for max floors reached turned into an integer so "normal" "humans" can read it.
        maxPointsReached = int(f'0x{hexMPR}', 0) # value for max points reached turned into an integer.
        return [fileLength, maxFloorReached, maxPointsReached]

async def setup(client:commands.Bot) -> None:
    """Initialize cog."""
    await client.add_cog(Road(client))

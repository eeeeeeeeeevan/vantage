# release if leaked 

from discord.ext import commands
from discord import Intents
from vantage import VANTAGE
import os

bot = commands.Bot(command_prefix=".", intents=Intents.default())

async def themethod():
    await bot.add_cog(VANTAGE(bot))

bot.themethod = themethod
bot.run(os.getenv("DISCORD_TOKEN"))
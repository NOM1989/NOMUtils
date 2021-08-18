from discord.ext import commands
import aiohttp
import discord

class Bored(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bored(self, ctx):
        """
        Makes a request to www.boredapi.com for an activity to do and displays it
        """
        async with aiohttp.ClientSession() as session:
            async with session.get('http://www.boredapi.com/api/activity/') as response:
                response = await response.json()
                print(response)
        embed = discord.Embed(colour = 0x2F3136, description=f'Report by {ctx.author.mention}')

def setup(bot):
    bot.add_cog(Bored(bot))

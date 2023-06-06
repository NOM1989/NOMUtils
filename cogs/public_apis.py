from discord.ext import commands
from .utils.context import Context
from datetime import datetime
from bot import NOMUtils
from os import getenv
import discord
import aiohttp
import re

class APIS(commands.Cog):
    def __init__(self, bot):
        self.bot: NOMUtils = bot
        self.SEARCH_LIMIT: int = 100
        self.BITLYAPI_KEY: str = getenv('BITLYAPI_KEY')

    @commands.command()
    async def bitsee(self, ctx: Context, bitlink: str = None):
        """Requests the long url from a bit.ly link,
        bitlink sourced from either passed argument
        or searches last SEARCH_LIMIT messages in channel for link"""

        bitlink_REGEX = r'(https?:\/\/)?((bit\.ly)\S*)\b'
        bitlink_search = None
        
        if bitlink == None:
            # Search channel for link
            async for message in ctx.channel.history(limit=self.SEARCH_LIMIT):
                bitlink_search = re.search(bitlink_REGEX, message.content)
                if bitlink_search:
                    break
        else:
            # Check it is a bit.ly link
            bitlink_search = re.search(bitlink_REGEX, bitlink)
            
        if bitlink_search:
            bitlink = bitlink_search.group(2)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.BITLYAPI_KEY}',
                    'Content-Type': 'application/json',
                }
                data = f'{{ "bitlink_id": "{bitlink}" }}'
                async with session.post('https://api-ssl.bitly.com/v4/expand', data=data, headers=headers) as response:
                    if response.ok:
                        result = await response.json()
                        date_time = datetime.fromisoformat(result['created_at'][:-2] + ':' + result['created_at'][-2:])
                        embed = discord.Embed(title=f'Lookup for: `{bitlink}`', description=result['long_url'], timestamp=date_time, color=discord.Colour.green())
                        embed.set_footer(text='Link created at')
                        return await ctx.send(embed=embed)

                    # When a bitly request does not return the 'ok' status
                    if ctx.args[2] != None:
                        await ctx.reply(f"{self.bot.my_emojis.question} - Invalid bit.ly link")

        return await ctx.message.add_reaction('🚫')

async def setup(bot):
    await bot.add_cog(APIS(bot))

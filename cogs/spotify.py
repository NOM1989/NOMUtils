from .utils.context import Context
from discord.ext import commands
from bot import NOMUtils
from os import getenv
import aiohttp
import discord
import base64
from time import time

class Spotify(commands.Cog):
    def __init__(self, bot):
        self.bot: NOMUtils = bot
        self.encoded_client_details: str = base64.b64encode(bytes(f"{getenv('CLIENT_ID')}:{getenv('CLIENT_SECRET')}", 'ascii')).decode('ascii')
        self.access_token: str = None
        self.token_expiration: float = 0

    async def cog_check(self, ctx: Context):
        return await self.bot.is_owner(ctx.author)

    async def refresh_token(self):
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': 'Basic ' + self.encoded_client_details,
            }
            # Body
            data = {
                'grant_type': 'client_credentials'
            }
            async with session.post('https://accounts.spotify.com/api/token', data=data, headers=headers) as response:
                # print(response)
                if response.ok:
                    response_json = await response.json()
                    self.access_token = response_json['access_token']
                    self.token_expiration = time() + response_json['expires_in']
                # else:
                    # print(await response.json())

    @commands.command()
    async def spotify(self, ctx: Context, *query: str):
        if time() >= self.token_expiration:
            await self.refresh_token()
        async with aiohttp.ClientSession() as session:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}',
            }
            params = {
                'q': ' '.join(query),
                'type': 'track',
                'limit': '1',
            }
            async with session.get('https://api.spotify.com/v1/search', params=params, headers=headers) as response:
                print(response)
                if response.ok:
                    response_json = await response.json()
                    await ctx.reply(response_json['tracks']['items'][0]['external_urls']['spotify'])
                else:
                    await ctx.reply(f"{self.bot.my_emojis.error} - An error occured: ```py\n{await response.json()}\n```")

async def setup(bot):
    await bot.add_cog(Spotify(bot))

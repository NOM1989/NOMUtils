from cogs.utils.utils import get_webook
from .utils.context import Context
from discord.ext import commands
from typing import Union
from bot import NOMUtils
import discord

class Name(commands.Cog):
    def __init__(self, bot):
        self.bot: NOMUtils = bot
        self.allowed = [
            361919376414343168,
            421362214558105611
        ]

    async def cog_check(self, ctx: Context):
        return ctx.author.id in self.allowed

    @commands.guild_only()
    @commands.command(hidden=True)
    async def sudo(self, ctx: Context, who: Union[discord.Member, discord.User], *, text=None):
        """Impersonate a user (must share a server with this bot)"""
        await ctx.message.delete()
        files = []
        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                files.append(await attachment.to_file())
        webhook = await get_webook(self.bot, ctx.channel)
        await webhook.send(content=text if text != None else '', username=who.display_name, avatar_url=who.display_avatar.url, files=files)

def setup(bot):
    bot.add_cog(Name(bot))
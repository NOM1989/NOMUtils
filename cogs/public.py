from discord.ext import commands
import discord
from asyncio import TimeoutError
from typing import Union

class Public(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # async def cog_check(self, ctx):
    #     return await self.bot.is_owner(ctx.author)
    #     # return not ctx.author.bot

    async def avatar_embed(self, mention, avatar_url):
        embed = discord.Embed(description=f'{mention}\'s Avatar', colour=0x2F3136)
        embed.set_image(url=avatar_url)
        return embed

    @commands.command(aliases=['pfp', 'avitar'])
    async def avatar(self, ctx, who: Union[discord.Member, discord.User]):
        msg = await ctx.reply(embed=await self.avatar_embed(who.mention, who.display_avatar.url), allowed_mentions = discord.AllowedMentions.none())
        if who.display_avatar != who.avatar:
            try:
                await msg.add_reaction('🔄')
                def check(reaction, user):
                    return user == ctx.message.author and str(reaction.emoji) == '🔄'

                try:
                    await self.bot.wait_for('reaction_add', timeout=60, check=check)
                except TimeoutError:
                    pass
                else:
                    await msg.edit(embed=await self.avatar_embed(who.mention, who.avatar.url), allowed_mentions = discord.AllowedMentions.none())
                try:
                    await msg.clear_reaction('🔄')
                except discord.Forbidden:
                    await msg.remove_reaction('🔄', msg.author)
            except:
                pass

def setup(bot):
    bot.add_cog(Public(bot))
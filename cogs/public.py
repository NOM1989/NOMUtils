from discord.ext import commands
import discord
from asyncio import TimeoutError
from typing import Union
from difflib import get_close_matches
from datetime import datetime
from random import choice

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
    async def avatar(self, ctx, *, who: Union[discord.Member, discord.User]):
        """
        Sends the passed users' avitar in an embed
        """
        msg = await ctx.reply(embed=await self.avatar_embed(who.mention, who.display_avatar.url), allowed_mentions = discord.AllowedMentions.none())
        if who.avatar != None and who.display_avatar != who.avatar:
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
            except discord.Forbidden:
                pass

    @avatar.error
    async def avatar_handler(self, ctx, error):
        """
        A local Error Handler, only listens for errors in avatar
        The global on_command_error will still be invoked after.
        """
        error_extra = f' - `{ctx.prefix}{ctx.invoked_with} <user>`'
        # Check if our required argument is missing
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'who':
                await ctx.reply(f"{self.bot.config['emojis']['error']} You must specify a **user**{error_extra}", allowed_mentions=discord.AllowedMentions.none())
                ctx.error_handled = True
        else:
            ctx.error_extra = error_extra

    @commands.command(aliases=['guild_emojis'])
    @commands.has_guild_permissions(manage_messages=True)
    async def emojis(self, ctx):
        """Sends a list of all the guilds' emojis"""
        to_send = ''
        for emoji in ctx.guild.emojis:
            string = f"{emoji} -- `<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}>`\n"
            if len(to_send + string) > 2000: 
                await ctx.send(to_send)
                to_send = ''
            else:
                to_send += string
        await ctx.send(to_send)


    @commands.group(name='is')
    async def question(self, ctx):
        """Replies yes or no to simple questions"""
    
    @question.command()
    async def it(self, ctx, *args):
        """Replies depending on day of week"""
        day_specials = {
            'friday': ('yes', 'among us fri-yay?! :partying_face:', '<:sus:822637858900148256>?', 'amongus?'),
            'wednesday': ('yes', 'my dudes')
        }
        if len(args) > 0:
            matches = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
            possible_match = get_close_matches(args[0], matches, n=1)
            if possible_match:
                day_today = datetime.today().strftime('%A').lower()
                if day_today == possible_match[0]:
                    await ctx.send(choice(day_specials[day_today]) if day_today in day_specials else 'yes')
                else:
                    await ctx.send('no')

def setup(bot):
    bot.add_cog(Public(bot))
from asyncio import TimeoutError, sleep
from difflib import get_close_matches
from .utils.context import Context
from discord.ext import commands
from datetime import datetime
from random import choice
from typing import Union
from io import BytesIO
import discord

class Public(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # async def cog_check(self, ctx):
    #     return await self.bot.is_owner(ctx.author)
    #     # return not ctx.author.bot

    # For future update of d.py
    # async def avatar_embed(self, who, avatar, *, reply=None, edit=None, msg=None):
    #     filename = 'avatar.png'

    #     with io.BytesIO() as buffer:
    #         await avatar.save(buffer)
    #         avatar_file = discord.File(buffer, filename=filename)
    #         embed = discord.Embed(description=f'{who.mention}\'s Avatar', colour=0x2F3136)
    #         embed.set_image(url=f'attachment://{filename}')
    #         if reply:
    #             msg = await reply(file=avatar_file, embed=embed, allowed_mentions=discord.AllowedMentions.none())
    #         else:
    #             await msg.remove_attachments(msg.attachments[0])
    #             await msg.add_files(avatar_file)
    #             msg = await edit(embed=embed, allowed_mentions=discord.AllowedMentions.none())
    #         return msg

    async def avatar_message(self, ctx, who, avatar):
        '''I convert the avatar to a file then upload that so that it is perminent,
        if we just used the url then it would be lost in the future (avatar change)'''
        filename = 'avatar'
        if avatar.is_animated():
            filename += '.gif'
        else:
            filename += '.png'
        async with ctx.typing():
            with BytesIO() as buffer:
                await avatar.save(buffer)
                avatar_file = discord.File(buffer, filename=filename)
                embed = discord.Embed(description=f'{who.mention}\'s Avatar', colour=0x2F3136)
                embed.set_image(url=f'attachment://{filename}')
                try:
                    return await ctx.reply(file=avatar_file, embed=embed, allowed_mentions=discord.AllowedMentions.none())
                except discord.errors.HTTPException:
                    pass #Secret way to cancel (deleting the invocation message)

    @commands.command(aliases=['pfp', 'avitar'])
    async def avatar(self, ctx, *, who: Union[discord.Member, discord.User] = None):
        """Sends the passed users' avitar in an embed or the author is user not"""
        # msg = await self.avatar_embed(who, who.display_avatar, reply=ctx.reply) #For future update of d.py
        if who == None:
            who = ctx.message.author
        msg = await self.avatar_message(ctx, who, who.display_avatar)
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
                    # msg = await self.avatar_embed(who, who.avatar, edit=msg.edit, msg=msg) #For future update of d.py
                    await msg.delete()
                    msg = await self.avatar_message(ctx, who, who.avatar)
                try:
                    await msg.clear_reaction('🔄')
                except discord.Forbidden:
                    await msg.remove_reaction('🔄', msg.author)
            except discord.Forbidden:
                pass

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
        if to_send:
            await ctx.send(to_send)

    @commands.command()
    async def emoji(self, ctx: commands.Context, emoji: discord.Emoji):
        """Sends the passed emoji in an embed"""
        filename = 'emoji'
        if emoji.animated:
            filename += '.gif'
        else:
            filename += '.png'
        async with ctx.typing():
            with BytesIO() as buffer:
                await emoji.save(buffer)
                emoji_file = discord.File(buffer, filename=filename)
                embed = discord.Embed(colour=0x2F3136)
                embed.set_image(url=f'attachment://{filename}')
                try:
                    await ctx.reply(file=emoji_file, embed=embed, allowed_mentions=discord.AllowedMentions.none())
                except discord.errors.HTTPException:
                    pass #Secret way to cancel (deleting the invocation message)

    @emoji.error
    async def emoji_handler(self, ctx, error):
        """
        A local Error Handler, only listens for errors in emoji
        The global on_command_error will still be invoked after.
        """
        # Check if the emoji is not found
        if isinstance(error, commands.EmojiNotFound):
            ctx.error_message = 'Emoji must be custom; emoji not recognised'
        elif isinstance(error, commands.MissingRequiredArgument):
            ctx.error_message = 'You must provide an emoji'
            ctx.error_add_usage = True

    @commands.group(name='is')
    async def question(self, ctx):
        """Replies yes or no to simple questions"""
        pass
        # free = ('free', '23')
        # possible_match = get_close_matches(args[1], free, n=1)
        # if possible_match in free:
        #     pdog = ('pdog', 'patrick', 'pdogger', 'pat')
        #     possible_match = get_close_matches(args[0], pdog, n=1)
        #     if args[0] == '<@!361919376414343168>' or possible_match in pdog:
        #         await ctx.send(f"yes{', pdog so free!' if randint(0,1) else  ''}")
        #     else:
        #         await ctx.send('no')
    
    @question.command()
    async def it(self, ctx, *args):
        """Replies depending on day of week"""
        day_specials = {
            'friday': ('yes', 'among us fri-yay?! :partying_face:', 'yes... <:sus:822637858900148256>?'),
            'wednesday': ('yes', 'yes, my dudes')
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

    @commands.command()
    async def search(self, ctx: Context, *, name_or_tag: str):
        # In the future make use of a channel tagging system (DB) to allow for custom tags on channels or use the channel description
        """Enter a possible channel name and the bot will provide a jump link to it if you have the appropriate permissions"""
        to_delete = [ctx.message]
        possible_channel = get_close_matches(name_or_tag, [getattr(channel, 'name') for channel in ctx.guild.text_channels], n=1)
        if possible_channel:
            channel = discord.utils.get(ctx.guild.text_channels, name=possible_channel[0])
            perms: discord.Permissions = channel.permissions_for(ctx.message.author)
            if perms.read_messages:
                to_delete.append(await ctx.reply(channel.mention, allowed_mentions=discord.AllowedMentions.none()))
        if len(to_delete) == 1:
            await ctx.message.add_reaction('🚫')
            # await ctx.reply('Sorry, that channel doesnt exist or you cannot view it', allowed_mentions=discord.AllowedMentions.none())
        
        await sleep(5)
        try:
            await ctx.message.channel.delete_messages(to_delete)
        except discord.Forbidden:
            pass

async def setup(bot):
    await bot.add_cog(Public(bot))

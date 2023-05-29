from discord.ext import commands
import discord
from time import time
from .utils.context import Context
from asyncio import sleep
from collections import Counter
import re


rog_server_id = 593542699081269248
admin_role_id = 691357082070286456 #The Council
owner_id = 421362214558105611

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_clear = 0
        self.green_emoji = self.bot.config['emojis']['green']

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)
        # return not ctx.author.bot

    @commands.command(hidden=True, aliases=['purge'])
    async def clear(self, ctx: Context, *, amount: int):
        """Clears the specified amount of messages"""
        # del_message_list = ctx.channel.purge(limit=amount) #If you want to get the messages deleted
        await ctx.message.delete()
        if amount <= 100:
            if time() - self.last_clear > 2:
                await ctx.channel.purge(limit=amount, before=ctx.message)
                self.last_clear = round(time(), 6)
            else:
                await ctx.send('Cleared within 2 seconds, assuming message repeated due to connection issues.', delete_after=8.0)
        else:
            await ctx.send('Amount > 100, assuming typo.', delete_after=8.0)
    
    @commands.command(hidden=True, aliases=['mpurge'])
    async def mclear(self, ctx: Context, *, target_m: discord.Message):
        """Clears up to a specified message"""
        deleted = await ctx.channel.purge(limit=100, after=target_m)
        await ctx.send(f'Deleted {len(deleted)} message(s)', delete_after=3)

    #Delete messages between certain messages
    @commands.command(hidden=True, aliases=['del'])
    async def delete(self, ctx: Context, m_from: discord.Message, m_to: discord.Message):
        '''Deletes messages within the 2 given messages'''
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=100, before=m_to, after=m_from)
        await ctx.send(f'Deleted {len(deleted)} message(s)', delete_after=3)

    #My inital cleanup command, but after some inspiration from R. Danny I redesigned it
    # @commands.command(aliases=['clean'])
    # async def cleanup(self, ctx):
    #     def check_bot(message):
    #         return message.author.bot

    #     deleted_messages = await ctx.channel.purge(limit=50, check=check_bot, before=ctx.message)
    #     deleted_summary = {}
    #     for message in deleted_messages:
    #         if message.author.name not in deleted_summary:
    #             deleted_summary[message.author.name] = 1
    #         else:
    #             deleted_summary[message.author.name] += 1

    #     display_removed = ''
    #     for user in deleted_summary:
    #         display_removed += f'\n- **{user}**: {deleted_summary[user]}'
    #     await ctx.send(f'{len(deleted_messages)} messages cleaned up.\n{display_removed}', delete_after=10)

    async def _cleanup_messages(self, ctx, search):
        prefixes = ('!', '?', '+', '.')
        regex_acceptable = ''.join(prefixes)

        def check_bot(message):
            #The regex matches a prefix followed by a char that is not one of the prefixes eg: '!!ping' will not be deleted but '!ping' will be - this means messages like '!!!' or '...' are not removed
            return message.author.bot or (len(message.content) > 1 and re.search(fr'[{regex_acceptable}][^{regex_acceptable}]', message.content[:2]))

        deleted_messages = await ctx.channel.purge(limit=search, check=check_bot, before=ctx.message)
        return Counter(message.author.display_name for message in deleted_messages)

    # #Add a check here if the server is rog, allow council else: owner only
    # @staticmethod
    # def rog_check(ctx):
    #     to_return = False
    #     if ctx.author.id == owner_id:
    #         to_return = True
    #     elif ctx.guild and ctx.guild.id == rog_server_id: #ROG
    #         # utils.get(message.author.roles, name="Nitro Booster") - A better way? Maybe implement later
    #         to_return = ctx.guild.get_role(admin_role_id) in ctx.author.roles #The council
    #     return to_return

    @commands.command(aliases=['clean'])
    # @commands.check(rog_check)
    async def cleanup(self, ctx: Context, search=60):
        '''
        Cleans up bot and invocation messages in a channel.

        If a search number is specified, it searches that many messages to delete.
        Search - min: 2, max: 1000. Default: 60
        '''
        
        search = min(max(2, search), 1000)

        users = await self._cleanup_messages(ctx, search)
        # users will look like this: Counter({'-ers!': 5}) #Display_name followed by the amount of their messages
        deleted_count = sum(users.values())
        #Now we build the display result
        removed_messages = [f"{deleted_count} message{'' if deleted_count == 1 else 's'} cleaned up."]
        if deleted_count: #If any messages were deleted display who's they were
            removed_messages.append('') #Adds a break when we later join them
            #The following lambda function (lambda x: x[1]) is equivalent to:
            '''
            def func_name(x):
                return x[1]

            key would be key=func_name
            '''
            users = sorted(users.items(), key=lambda x: x[1], reverse=True)
            removed_messages.extend(f'- **{author}**: {count}' for author, count in users)

        await ctx.send('\n'.join(removed_messages), delete_after=10)
        await sleep(10)
        await ctx.message.delete()

    # @commands.is_owner()
    # @commands.command(hidden=True, aliases=['antispam', 'anti_spam', 'remove_spam'])
    # async def removespam(self, ctx, *, target_m: discord.Message):
    #     """Clears all instances of a specified message from the mesages author in the last week"""
    #     sleep_time = 0.5
    #     reply = await ctx.reply(f'<a:typing:931524283065319446>  Scanning **{len(ctx.guild.text_channels)}** channels `max eta: {len(ctx.guild.text_channels)*sleep_time} sec`', allowed_mentions = discord.AllowedMentions.none())
    #     deleted = 0
    #     for text_channel in ctx.guild.text_channels:
    #         last_msg = text_channel.last_message
    #         if last_msg:
    #             if last_msg.author == target_m.author and last_msg.content == target_m.content:
    #                 await last_msg.delete()
    #                 deleted += 1
    #                 await sleep(sleep_time)
    #     await reply.edit(f'{self.green_emoji} Deleted **{deleted}** message(s) `[in {deleted} channels]`', allowed_mentions = discord.AllowedMentions.none())

    @commands.command()
    async def nick(self, ctx: Context, who: discord.Member, *, nickname: str = None):
        if nickname == None:
            nickname = None
        await who.edit(nick=nickname)

    @nick.error
    async def nick_handler(self, ctx, error):
        """
        A local Error Handler, only listens for errors in nick
        The global on_command_error will still be invoked after.
        """
        if isinstance(error, commands.MissingRequiredArgument):
            ctx.error_message = 'You must provide a member'
            ctx.error_add_usage = True

async def setup(bot):
    await bot.add_cog(Admin(bot))

from discord.ext import commands
import discord
from time import time

from collections import Counter
import re

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_clear = 0

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)
        # return not ctx.author.bot

    @commands.is_owner()
    @commands.command(hidden=True, aliases=['purge'])
    async def clear(self, ctx, *, amount: int):
        """Clears the specified amount of messages"""
        # del_message_list = ctx.channel.purge(limit=amount) #If you want to get the messages deleted
        if amount <= 50:
            if time() - self.last_clear > 3:
                await ctx.channel.purge(limit=amount+1, before=ctx.message) #+1 to remove the cmd message
                self.last_clear = round(time(), 6)
            else:
                await ctx.message.delete()
                await ctx.send('Cleared within 3 seconds, assuming message repeted due to connection issues.', delete_after=8.0)
        else:
            await ctx.message.delete()
            await ctx.send('Amount > 50, assuming typo.', delete_after=8.0)
    
    #Delete messages between certain messages
    @commands.is_owner()
    @commands.command(hidden=True, aliases=['del'])
    async def delete(self, ctx, m_from: discord.Message, m_to: discord.Message):
        '''
        Deletes messages within the 2 given messages
        '''
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=200, before=m_to, after=m_from)
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

    #Add a check here if the server is rog, allow council else: owner only
    def rog_check(ctx):
        if ctx.author.id == 123:
            return True
        elif ctx.guild:
            if ctx.guild.id == 123:
                return 'council' in ctx.author.roles
            else:
                return False
        else:
            return False

    
    @commands.command()
    async def cleanup(self, ctx, search=60):
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
            #The following lambda function (lambda x: x[1]) is equivilent to:
            '''
            def func_name(x):
                return x[1]

            key would be key=func_name
            '''
            users = sorted(users.items(), key=lambda x: x[1], reverse=True)
            removed_messages.extend(f'- **{author}**: {count}' for author, count in users)

        await ctx.send('\n'.join(removed_messages), delete_after=10)

def setup(bot):
    bot.add_cog(Admin(bot))
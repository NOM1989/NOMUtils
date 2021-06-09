from re import split
from discord.ext import tasks, commands
import discord
from random import randint

from gensim.summarization.summarizer import summarize

class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_ctx = None

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)
    
    def cog_unload(self):
        self.vc_running.cancel()

    @tasks.loop(seconds=2.2)
    async def vc_evasion(self):
        ctx = self.current_ctx
        if ctx.author.voice: #User is still in a vc
            category_count = len(ctx.guild.categories)
            if category_count > 1: #This only works if there is more than one category
                target_category = ctx.author.voice.channel.category
                while target_category == ctx.author.voice.channel.category: #If you get unlucky could cause a temporary ifinate loop
                    target_category = ctx.guild.categories[randint(0, category_count-1)]
                    print(target_category.name, ctx.author.voice.channel.category.name)
                await ctx.author.voice.channel.move(end=True, category=target_category, sync_permissions=False)
        else: #The user has left the vc
            self.vc_evasion.cancel()
            await ctx.send(f'{ctx.author.mention} :x: You left the vc, so it has stoped running')

    @commands.command(hidden=True)
    async def vcrun(self, ctx):
        """Causes the vc to move around the server"""
        #Maybe add a thing where it returns it to og pos
        if ctx.author.voice:
            if self.vc_evasion.is_running():
                self.current_ctx = None
                self.vc_evasion.stop()
                await ctx.send(':person_standing: Your vc is no longer on the run')
            else:
                self.current_ctx = ctx
                self.vc_evasion.start()
                await ctx.send(':person_running: Your vc is now on the run')
        else:
            await ctx.send('You are not in vc, so it cannot run')

    @commands.command(hidden=True, aliases=['vcint'])
    async def vcinterval(self, ctx, *, new_interval):
        # """Causes the vc to move around the server"""
        if self.vc_evasion.is_running(): #The interval is changable
            try:
                new_interval = float(new_interval)
            except:
                new_interval = False
                await ctx.send('`new_interval` was not an integer')
            if new_interval:
                new_interval = float(new_interval)
                self.vc_evasion.change_interval(seconds=new_interval)
                await ctx.send(f'Set interval to `{new_interval}`')
        else:
            await ctx.send('Your vc is not running')

    async def split_long_text(self, sentances_list):
        chunked_list = []
        current_large_chunk = ''
        for sentance in sentances_list:
            if len(current_large_chunk + sentance) < 2000: #Discord message limit
                current_large_chunk = current_large_chunk + sentance + '\n'
            else:
                chunked_list.append(current_large_chunk)
                current_large_chunk = ''
        chunked_list.append(current_large_chunk) #Add it once more as it has gone through all the sentances
        return chunked_list

    @commands.command(hidden=True, aliases=['summarize'])
    async def summary(self, ctx, member: discord.Member = None, start_message: discord.Message = None):
        await ctx.message.delete()
        if member and start_message:
            members_messages_txt = ''
            async for message in ctx.channel.history(limit=2500, oldest_first=True, after=start_message):
                if message.author == member:
                    members_messages_txt = members_messages_txt + message.content + '\n' #Gensim handles converting newlines into sentance breaks
            
            # print(members_messages_txt)
            # Test message id: 795938892964298762-852186939019755560
            summary_list = summarize(members_messages_txt, split=True)
            # print(summary_list)
            print(summary_list)
            if summary_list:
                summary_list = await self.split_long_text(summary_list) #Reusing the old var to hopefully reduce memory usage? idk if it works like that tho
                await ctx.message.author.send(f'**\-\-\-\nSummary of {member.name}\'s last messages in {ctx.guild.name}-{ctx.channel.name}**')
                for chunk in summary_list:
                    await ctx.message.author.send(chunk)
            else:
                await ctx.message.author.send(f'Could not summarise {member.name}\'s last messages in {ctx.guild.name}-{ctx.channel.name}')

        elif member == None:
            await ctx.message.author.send('A user must be specified `cmd member start_message`')
        elif start_message == None:
            await ctx.message.author.send('A starting message must be specified `cmd member start_message`')

def setup(bot):
    bot.add_cog(Tools(bot))

from discord.ext import commands
import discord

#Requires: gensim==3.8.3
from gensim.summarization.summarizer import summarize

class Summary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

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
    async def summary(self, ctx, member: discord.Member, start_message: discord.Message = None):
        '''
        Creates a summary of the last messages of a specific user and DMs it to you
        '''
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
    bot.add_cog(Summary(bot))
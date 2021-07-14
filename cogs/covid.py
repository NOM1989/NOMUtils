from discord.ext import commands
import discord

from asyncio import sleep

class Covid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reporting_channel = 864900492290293800 #Reports (in ROG)
        # self.reporting_channel = 852214751949226015 #Test channel
        self.cannot_report = []

    async def cog_check(self, ctx):
        if ctx.guild and ctx.guild.id == 593542699081269248: #ROG
        # if ctx.guild and ctx.guild.id == 776206487395631145: #Test Server
            return True
        else:
            return False

    @commands.command()
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def report(self, ctx):
        """
        Sends reports to a specified channel
        
        Format: first_name last_name, Result, (optional)Extra info
        """
        if ctx.author.id not in self.cannot_report:
            reply_sent = False
            content = ctx.message.content.replace('?report', '')
            comma_count = content.count(',')
            embed = discord.Embed(colour = 0x2F3136, description=f'Report by {ctx.author.mention}')
            if comma_count == 0: #Attempt to split by spaces and first 2 indexes are name, third is result and the rest are extra
                split_content = content.split()
                if len(split_content) >= 3: #At least 3 for name and result
                    embed.add_field(name='Name', value='{0[0]} {0[1]}'.format(split_content))
                    embed.add_field(name='Result', value=split_content[2])
                    if len(split_content) > 3: #Extras passed
                        del split_content[:3]
                        embed.add_field(name='Extra', value=' '.join(split_content))
                else:
                    reply_sent = True
                    await ctx.send('Not enough parameters, use the format: `first_name last_name, Result, (optional)Extra info`')
                    self.report.reset_cooldown(ctx)
            else: #Name and result passed
                split_content = content.split(',')
                embed.add_field(name='Name', value=split_content[0])
                embed.add_field(name='Result', value=split_content[1])
                if comma_count > 1: #Extras passed
                    embed.add_field(name='Extra', value=split_content[2])

            if not reply_sent:
                reporting_channel = self.bot.get_channel(self.reporting_channel)
                await reporting_channel.send(embed=embed)
                await ctx.send('Report successful!', embed=embed, delete_after=10)
                await sleep(10)
                await ctx.message.delete()
        else:
            await ctx.send('Report Failed.', delete_after=10)
            self.report.reset_cooldown(ctx)
            await sleep(10)
            await ctx.message.delete()

    @commands.is_owner()
    @commands.command(hidden=True)
    async def block(self, ctx, member: discord.Member):
        await ctx.message.delete()
        if member.id not in self.cannot_report:
            self.cannot_report.append(member.id)
    
    @commands.is_owner()
    @commands.command(hidden=True)
    async def unblock(self, ctx, member: discord.Member):
        await ctx.message.delete()
        if member.id in self.cannot_report:
            self.cannot_report.remove(member.id)

def setup(bot):
    bot.add_cog(Covid(bot))
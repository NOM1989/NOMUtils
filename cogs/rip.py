from discord.ext import commands
import discord

from random import choice

class RIP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild and ctx.guild.id == 593542699081269248: #ROG
        # if ctx.guild and ctx.guild.id == 776206487395631145: #Test Server
            return True
        else:
            return False

    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def rip(self, ctx, *, channel: discord.TextChannel = None):
        rip_emojis = ('💀', '🕯️', '🙏', '🪦', '😪', '😩', '😤', '🌹', '🧎‍♂️', '👏', '🇷ℹ️🅿️', '🏺', '🧲')
        if channel == None:
            for channel in ctx.guild.channels:
                already_changed = False
                for emoji in rip_emojis:
                    if emoji in channel.name:
                        already_changed = True
                if not already_changed:
                    break

        new_name = '{0} {1} {0}'.format(choice(rip_emojis), channel.name)
        if len(new_name) <= 100:
            await channel.edit(name=new_name)
        else:
            await ctx.send('That channel name is too long already! Try a different one')
            self.rip.reset_cooldown(ctx)



def setup(bot):
    bot.add_cog(RIP(bot))
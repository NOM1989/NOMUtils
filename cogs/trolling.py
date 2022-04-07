from discord.ext import commands
import discord

class Trolling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ignored_guild_ids: list[int] = [749665566884757566]

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.TextChannel):
        if channel.guild.id not in self.guild_ids:
            await channel.send('first')

def setup(bot):
    bot.add_cog(Trolling(bot))
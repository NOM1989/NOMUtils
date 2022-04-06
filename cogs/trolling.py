from discord.ext import commands
import discord

class Trolling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_ids: list[int] = [593542699081269248]

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.TextChannel):
        if channel.guild.id in self.guild_ids:
            await channel.send('first')

def setup(bot):
    bot.add_cog(Trolling(bot))
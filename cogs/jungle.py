from discord.ext import commands
# import discord

class Jungle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rog_id = 593542699081269248
        self.jungle_role_id = 933493052331413545

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)
        # return not ctx.author.bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild and member.guild.id == self.rog_id:
            role = member.guild.get_role(self.jungle_role_id)
            await member.add_roles(role, reason='ooh ooh ahh ahh 🐒')

    # discord.on_member_join(member)
    # discord.on_member_remove(member)

def setup(bot):
    bot.add_cog(Jungle(bot))
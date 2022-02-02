from discord.ext import commands
import discord
from asyncio import TimeoutError
from typing import Union

class Public(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # async def cog_check(self, ctx):
    #     return await self.bot.is_owner(ctx.author)
    #     # return not ctx.author.bot

    async def avatar_embed(self, mention, avatar_url):
        embed = discord.Embed(description=f'{mention}\'s Avatar', colour=0x2F3136)
        embed.set_image(url=avatar_url)
        return embed

    @commands.command(aliases=['pfp', 'avitar'])
    async def avatar(self, ctx, *, who: Union[discord.Member, discord.User]):
        """
        Sends the passed users' avitar in an embed
        """
        msg = await ctx.reply(embed=await self.avatar_embed(who.mention, who.display_avatar.url), allowed_mentions = discord.AllowedMentions.none())
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
                    await msg.edit(embed=await self.avatar_embed(who.mention, who.avatar.url), allowed_mentions = discord.AllowedMentions.none())
                try:
                    await msg.clear_reaction('🔄')
                except discord.Forbidden:
                    await msg.remove_reaction('🔄', msg.author)
            except discord.Forbidden:
                pass

    @avatar.error
    async def avatar_handler(self, ctx, error):
        """
        A local Error Handler, only listens for errors in avatar
        The global on_command_error will still be invoked after.
        """
        error_extra = f' - `{ctx.prefix}{ctx.invoked_with} <user>`'
        # Check if our required argument is missing
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'who':
                await ctx.reply(f"{self.bot.config['emojis']['error']} You must specify a **user**{error_extra}", allowed_mentions=discord.AllowedMentions.none())
                ctx.error_handled = True
        else:
            ctx.error_extra = error_extra

    @commands.command(aliases=['guild_emojis'])
    @commands.guild_only()
    async def emojis(self, ctx):
        """Sends a list of all the guilds' emojis"""
        emoji_list = []
        for emoji in ctx.guild.emojis:
            emoji_list.append(f"{emoji} -- `<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}>`")
        await ctx.reply('\n'.join(emoji_list), allowed_mentions=discord.AllowedMentions.none())
        # Needs updating and limit usage to only ppl with manage messages (bypass for me ofc)

def setup(bot):
    bot.add_cog(Public(bot))
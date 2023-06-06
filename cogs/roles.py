from .utils.context import Context
from discord.ext import commands
from datetime import timedelta
from asyncio import sleep
from bot import NOMUtils
import discord

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot: NOMUtils = bot
        self.tmp_role_storage = {}
        self.sleep_time = 0.5

    async def clear_user_roles(self, member):
        origional_roles = list(member.roles)
        replace_roles = []
        for role in member.roles:
            if len(replace_roles) < 1:
                replace_roles.append(role) # Isolate the @eveyone role for that server
                break
        try:
            await member.edit(roles=replace_roles)
            self.tmp_role_storage[str(member.id)] = origional_roles
            return True
        except discord.errors.Forbidden:
            return False

    async def replace_user_roles(self, member):
        try:
            await member.edit(roles=self.tmp_role_storage[str(member.id)])
            del self.tmp_role_storage[str(member.id)]
            return True
        except discord.errors.Forbidden:
            return False

    @commands.command(hidden=True, aliases=['troll', 'poofers'])
    async def clear_roles(self, ctx: Context, member: discord.Member):
        """Clears the members roles (temp stores them so they can be returned later)"""
        if str(member.id) not in self.tmp_role_storage:
            await self.clear_user_roles(member)
            if ctx.invoked_with == 'poofers':
                reply = 'Poof! :dash:'
            else:
                reply = 'When the roles are gone :flushed:'
        else:
            reply = 'Crisis averted :sunglasses:'
        await ctx.reply(reply)

    @commands.command(hidden=True, aliases=['unpoof', 'return_roles', 'untroll'])
    async def replace_roles(self, ctx: Context, member: discord.Member):
        """Restores cleared roles"""
        if str(member.id) in self.tmp_role_storage:
            await self.replace_user_roles(member)
            await ctx.message.add_reaction('🤞')
        else:
            reply = 'Nothing to replace! :grimacing:'
            if ctx.guild.get_member(691299852352618620): #If soham is in the channel, blame him. (thats Soham's id)
                reply = reply + ' Blame Soham.'
            await ctx.reply(reply)


    @commands.group(aliases=['massrole'])
    @commands.guild_only()
    async def mass_role(self, ctx):
        pass

    @mass_role.command(aliases=['add'])
    async def give(self, ctx: Context, role: discord.Role, *, reason=None):
        msg = await ctx.reply(f'Queued `add role` to **~{ctx.guild.member_count} members**\n  --> Eta: **{str(timedelta(seconds=int(ctx.guild.member_count*self.sleep_time)))}**')
        count = 0
        for member in ctx.guild.members:
            if role not in member.roles:
                await member.add_roles(role, reason=reason)
                count += 1
                await sleep(self.sleep_time)
        await msg.edit(content=f"{self.bot.my_emojis.check} `Added` {role.mention} to **{count} members** :grimacing:", allowed_mentions=discord.AllowedMentions.none())

    @mass_role.command(aliases=['take'])
    async def remove(self, ctx: Context, role: discord.Role, *, reason=None):
        msg = await ctx.reply(f'Queued `remove role` to **~{ctx.guild.member_count} members**\n  --> Eta: **{str(timedelta(seconds=int(ctx.guild.member_count*self.sleep_time)))}**')
        count = 0
        for member in ctx.guild.members:
            if role in member.roles:
                await member.remove_roles(role, reason=reason)
                count += 1
                await sleep(self.sleep_time)
        await msg.edit(content=f"{self.bot.my_emojis.check} `Removed` {role.mention} from **{count} members** :grimacing:", allowed_mentions=discord.AllowedMentions.none())

    @mass_role.command()
    async def clear(self, ctx: Context):
        msg = await ctx.reply(f'Queued `clear roles` to **~{ctx.guild.member_count} members**\n  --> Eta: **{str(timedelta(seconds=int(ctx.guild.member_count*self.sleep_time)))}**')
        count = 0
        for member in ctx.guild.members:
            if len(member.roles) > 1:
                result = await self.clear_user_roles(member)
                if result:
                    count += 1
                    await sleep(self.sleep_time)
        await msg.edit(content=f"{self.bot.my_emojis.check} `Cleared` roles from **{count} members** :grimacing:", allowed_mentions=discord.AllowedMentions.none())

    @mass_role.command()
    async def replace(self, ctx: Context):
        msg = await ctx.reply(f'Queued `replace roles` to **~{ctx.guild.member_count} members**\n  --> Eta: **{str(timedelta(seconds=int(ctx.guild.member_count*self.sleep_time)))}**')
        count = 0
        for member in ctx.guild.members:
            if str(member.id) in self.tmp_role_storage:
                result = await self.replace_user_roles(member)
                if result:
                    count += 1
                    await sleep(self.sleep_time)
        await msg.edit(content=f"{self.bot.my_emojis.check} `Replaced` roles of **{count} members** :grimacing:", allowed_mentions=discord.AllowedMentions.none())


async def setup(bot):
    await bot.add_cog(Roles(bot))

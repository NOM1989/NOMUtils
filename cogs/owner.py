from discord.ext import commands
from time import time

# To do: https://github.com/Rapptz/RoboDanny/blob/f37e3b536fec0c5b70954c0be6850027010b77d5/cogs/admin.py#L180

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(hidden=True)
    async def ping(self, ctx):
        await ctx.send('Pong! `Latency: {}ms`'.format(round(self.bot.latency * 1000)))

    @commands.command(hidden=True, aliases=['close'])
    async def shutdown(self, ctx):
        await ctx.send('`Closing connection...`')
        await self.bot.close()

    @commands.command(hidden=True)
    async def load(self, ctx, *, module):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except commands.ExtensionError as e:
            module = f'cogs.{module}'
            try:
                self.bot.load_extension(module)
            except commands.ExtensionError as e:
                await ctx.send(f'{e.__class__.__name__}: {e}')
            else:
                await ctx.send(f'\N{OK HAND SIGN} `Loaded: {module}`')
        else:
            await ctx.send(f'\N{OK HAND SIGN} `Loaded: {module}`')

    @commands.command(hidden=True)
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except commands.ExtensionError as e:
            module = f'cogs.{module}'
            try:
                self.bot.unload_extension(module)
            except commands.ExtensionError as e:
                await ctx.send(f'{e.__class__.__name__}: {e}')
            else:
                await ctx.send(f'\N{OK HAND SIGN} `Unloaded: {module}`')
        else:
            await ctx.send(f'\N{OK HAND SIGN} `Unloaded: {module}`')

    @commands.command(hidden=True)
    async def reload(self, ctx, *, module):
        """Reloads a module."""
        try:
            self.bot.reload_extension(module)
        except commands.ExtensionError as e:
            module = f'cogs.{module}'
            try:
                self.bot.reload_extension(module)
            except commands.ExtensionError as e:
                await ctx.send(f'{e.__class__.__name__}: {e}')
            else:
                await ctx.send(f'\N{OK HAND SIGN} `Reloaded: {module}`')
        else:
            await ctx.send(f'\N{OK HAND SIGN} `Reloaded: {module}`')

    @commands.command(aliases=['fuckoff'])
    async def leave(self, ctx):
        await ctx.send('later l0$$ers')
        await ctx.guild.leave()

def setup(bot):
    bot.add_cog(Owner(bot))
from discord.ext import commands
from time import time

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_clear = None

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

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
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    async def reload(self, ctx, *, module):
        """Reloads a module."""
        try:
            self.bot.reload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True, aliases=['purge'])
    async def clear(self, ctx, *, amount: int):
        """Clears the specified amount of messages"""
        # del_message_list = ctx.channel.purge(limit=amount) #If you want to get the messages deleted
        if amount <= 50:
            if time() - self.last_clear > 3:
                await ctx.channel.purge(limit=amount+1) #+1 to remove the cmd message
                self.last_clear = round(time(), 6)
            else:
                await ctx.message.delete()
                await ctx.send('Cleared within 3 seconds, assuming message repeted due to connection issues.', delete_after=8.0)
        else:
            await ctx.message.delete()
            await ctx.send('Amount > 50, assuming typo.', delete_after=8.0)

def setup(bot):
    bot.add_cog(Admin(bot))
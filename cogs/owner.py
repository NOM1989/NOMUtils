from .utils.context import Context
from discord.ext import commands
from bot import NOMUtils
import discord

# To do: https://github.com/Rapptz/RoboDanny/blob/f37e3b536fec0c5b70954c0be6850027010b77d5/cogs/admin.py#L180


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot: NOMUtils = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(hidden=True)
    async def ping(self, ctx: Context):
        await ctx.send("Pong! `Latency: {}ms`".format(round(self.bot.latency * 1000)))

    @commands.command(hidden=True, aliases=["close"])
    async def shutdown(self, ctx):
        await ctx.send("`Closing connection...`")
        await self.bot.close()

    @commands.command(hidden=True)
    async def load(self, ctx, *, module):
        """Loads a module."""
        try:
            await self.bot.load_extension(module)
        except commands.ExtensionError as e:
            module = f"cogs.{module}"
            try:
                await self.bot.load_extension(module)
            except commands.ExtensionError as e:
                await ctx.send(f"{e.__class__.__name__}: {e}")
            else:
                await ctx.send(f"\N{OK HAND SIGN} `Loaded: {module}`")
        else:
            await ctx.send(f"\N{OK HAND SIGN} `Loaded: {module}`")

    @commands.command(hidden=True)
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        try:
            await self.bot.unload_extension(module)
        except commands.ExtensionError as e:
            module = f"cogs.{module}"
            try:
                await self.bot.unload_extension(module)
            except commands.ExtensionError as e:
                await ctx.send(f"{e.__class__.__name__}: {e}")
            else:
                await ctx.send(f"\N{OK HAND SIGN} `Unloaded: {module}`")
        else:
            await ctx.send(f"\N{OK HAND SIGN} `Unloaded: {module}`")

    @commands.command(hidden=True)
    async def reload(self, ctx, *, module):
        """Reloads a module."""
        try:
            await self.bot.reload_extension(module)
        except commands.ExtensionError as e:
            module = f"cogs.{module}"
            try:
                await self.bot.reload_extension(module)
            except commands.ExtensionError as e:
                await ctx.send(f"{e.__class__.__name__}: {e}")
            else:
                await ctx.send(f"\N{OK HAND SIGN} `Reloaded: {module}`")
        else:
            await ctx.send(f"\N{OK HAND SIGN} `Reloaded: {module}`")

    @commands.command()
    async def cogs(self, ctx: Context):
        """Lists all loaded cogs"""
        embed = discord.Embed(
            title="Loaded Cogs",
            description=" :gear: " + "\n :gear: ".join(self.bot.extensions),
        )
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(name="commands")
    async def list_commands(self, ctx: Context):
        embed = discord.Embed(
            title="Loaded Cogs",
        )

        for cog in self.bot.cogs:
            cog = self.bot.get_cog(cog)

            command_checks = []
            for cmd in cog.get_commands():
                command_checks.append(f'{cmd.name.upper()} - {" ".join(["cog_check"] if cog._get_overridden_method(cog.cog_check) else [] + [check.__qualname__.split(".")[0] for check in cmd.checks])}')

            embed.add_field(name=cog.qualified_name, value="\n".join(command_checks))

        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(aliases=["fuckoff"])
    async def leave(self, ctx):
        await ctx.send("later l0$$ers")
        await ctx.guild.leave()


async def setup(bot):
    await bot.add_cog(Owner(bot))

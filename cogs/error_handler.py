"""
If you are not using this inside a cog, add the event decorator e.g:
@bot.event
async def on_command_error(ctx, error)
For examples of cogs see:
https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
For a list of exceptions:
https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#exceptions
"""
from random import choice, randint

from bot import NOMUtils
from .utils.context import Context
from discord.ext import commands
from inspect import Parameter
from asyncio import sleep
import traceback
import datetime
import discord
import sys


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: NOMUtils = bot

    # def add_extra(self, ctx: Context):
    #     return f' {ctx.error_message}' if ctx.error_message else ''

    def get_cmd_usage(self, ctx: Context):
        """Creates a string describing the usage of the command"""
        usage = f"{ctx.prefix}{ctx.invoked_with}"
        ctx.command.params.values()
        for param in ctx.command.params.values():
            if param.name not in ("self", "ctx"):
                if param.default == Parameter.empty:
                    usage += f" <{param.name}>"
                else:
                    usage += f" [{param.name}]"
        return usage

    async def send_error(self, ctx: Context, *, emoji: str = None, default_text: str = None):
        """Sends an error to the user with optional extra info"""
        to_send = f"{emoji if emoji else self.bot.my_emojis.error} "
        try:
            to_send += ctx.error_message or default_text
        except TypeError:
            raise TypeError("WARNING: Bad usage of error handling, neither ctx.error_message or default_text was provided")
        # Add any additional error info I want displayed to ctx.error_message = error_message - see public.py for eg
        to_send += f" - `{self.get_cmd_usage(ctx)}`" if ctx.error_add_usage else ""
        await ctx.reply(to_send, allowed_mentions=discord.AllowedMentions.none())

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: Context, error: commands.CommandError
    ):
        """The event triggered when an error is raised while invoking a command."""

        # This prevents any commands with local handlers being handled here in on_command_error.
        # if hasattr(ctx.command, 'on_error'):
        # return

        ## Better implimentation ##
        # https://discord.com/channels/336642139381301249/381965515721146390/938184509025816627
        # my usual recommended solution here is anywhere you handle an error, assign context.error_handled or some other attribute
        # in "upper" error handlers (cog and global), use hasattr to check if the attr exists
        # if it does, don't do anything with the error
        # if you have or want a custom context, set it in the __init__ and you can skip the ugly hasattr and just check the attr
        ## Add: ctx.error_handled = True in any local error handlers

        if hasattr(ctx, "error_handled") and ctx.error_handled:
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ctx.error_message = getattr(ctx, "error_message", None)
        ctx.error_add_usage = getattr(ctx, "error_add_usage", False)

        ignored = (commands.CommandNotFound,)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, "original", error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            ctx.error_add_usage = True
            await self.send_error(ctx, default_text="Invalid usage")
            # text = f"{error_base}{self.add_extra(ctx)}{self.add_usage(ctx)}"
            # await ctx.reply(text, allowed_mentions=discord.AllowedMentions.none())
            # await ctx.send(f"`{error.__class__.__name__}` - \'**{error.param}**\'{str(error).strip(str(error.param))}")

        elif (
            isinstance(error, commands.BadUnionArgument) and error.param.name == "who" # When using a member/user union
        ):  # Used when converting to a discord member or user Object
            await self.send_error(
                ctx, emoji=self.bot.my_emojis.question, default_text="Sorry, I couldn't recognise that user"
            )

        elif (
            isinstance(error, commands.MemberNotFound) # When converting to discord.member
        ):
            await self.send_error(
                ctx, emoji=self.bot.my_emojis.question, default_text="Sorry, I couldn't find that member"
            )


        # I would put this in ignored but I will probably forget then not know why something isnt working
        elif isinstance(error, commands.CheckFailure):
            print(
                f"Ignoring exception in command {ctx.command}:\n  {error.__class__.__name__}: {error}",
                file=sys.stderr,
            )

        elif isinstance(error, commands.DisabledCommand):
            await self.send_error(
                ctx, default_text=f"Sorry, `{ctx.command.name}` has been disabled."
            )

        # See ?tag commands on cooldown
        elif isinstance(error, commands.CommandOnCooldown):
            if (
                ctx.command.qualified_name == "report"
            ):  # Check if the command being invoked is 'report'
                await ctx.send(
                    f"To prevent spam, you must wait {datetime.timedelta(seconds=round(error.retry_after))} before another report.",
                    delete_after=10,
                )
                await sleep(10)
                await ctx.message.delete()
            if ctx.command.qualified_name == "rip":
                await ctx.send(
                    f"You may only change one channel name per hour! ({datetime.timedelta(seconds=round(error.retry_after))} remaining)"
                )

        # elif isinstance(error, commands.NoPrivateMessage):
        #     try:
        #         await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        #     except discord.HTTPException:
        #         pass

        # For this error example we check to see where it came from...
        # elif isinstance(error, commands.BadArgument):
        #     if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
        #         await ctx.send('I could not find that member. Please try again.')


        # Don't display errors with a message in the console, just send in discord
        elif ctx.error_message:
            await self.send_error(ctx)

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print(
                "Ignoring exception in command {}:".format(ctx.command), file=sys.stderr
            )
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )
            error_flairs = (
                "ripperoni pepperoni",
                "damn",
                "sorry",
                "smh",
                "rip",
                "welp",
            )
            flair = f"{choice(error_flairs)}, a" if randint(0, 1) else "A"
            await self.send_error(
                ctx,
                default_text=f"{flair}n error occurred: `{error.__class__.__name__}: {error}`",
            )

    """Below is an example of a Local Error Handler for our command do_repeat"""

    # @commands.command(name='repeat', aliases=['mimic', 'copy'])
    # async def do_repeat(self, ctx, *, inp: str):
    #     """A simple command which repeats your input!
    #     Parameters
    #     ------------
    #     inp: str
    #         The input you wish to repeat.
    #     """
    #     await ctx.send(inp)

    # @do_repeat.error
    # async def do_repeat_handler(self, ctx, error):
    #     """A local Error Handler for our command do_repeat.
    #     This will only listen for errors in do_repeat.
    #     The global on_command_error will still be invoked after.
    #     """

    #     # Check if our required argument inp is missing.
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         if error.param.name == 'inp':
    #             await ctx.send("You forgot to give me input to repeat!")


async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))

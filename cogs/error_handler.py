"""
If you are not using this inside a cog, add the event decorator e.g:
@bot.event
async def on_command_error(ctx, error)
For examples of cogs see:
https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
For a list of exceptions:
https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#exceptions
"""
import discord
import traceback
import sys
from discord.ext import commands
import datetime
from asyncio import sleep
from random import choice, randint

class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"`{error.__class__.__name__}` - \'**{error.param}**\'{str(error).strip(str(error.param))}")

        # I would put this in ignored but I will probably forget then not know why something isnt working
        elif isinstance(error, commands.CheckFailure):
            print(f'Ignoring exception in command {ctx.command}:\n  {error.__class__.__name__}: {error}', file=sys.stderr)

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')
        
        #See ?tag commands on cooldown
        elif isinstance(error, commands.CommandOnCooldown):
            if ctx.command.qualified_name == 'report':  # Check if the command being invoked is 'report'
                await ctx.send(f"To prevent spam, you must wait {datetime.timedelta(seconds=round(error.retry_after))} before another report.", delete_after=10)
                await sleep(10)
                await ctx.message.delete()
            if ctx.command.qualified_name == 'rip':
                await ctx.send(f'You may only change one channel name per hour! ({datetime.timedelta(seconds=round(error.retry_after))} remaining)')

        # elif isinstance(error, commands.NoPrivateMessage):
        #     try:
        #         await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        #     except discord.HTTPException:
        #         pass

        # For this error example we check to see where it came from...
        # elif isinstance(error, commands.BadArgument):
        #     if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
        #         await ctx.send('I could not find that member. Please try again.')

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            error_flairs = (
                'ripperoni pepperoni',
                'damn',
                ':expressionless:',
                'pop!',
                'sorry',
                '<@421362214558105611> pls fix',
                'Someone fix this',
                'smh',
                'this wasnt expected',
                ':shushing_face:',
                'rip',
                'no its not dead - but',
                'ok maybe its a bit broken',
                f'{ctx.author.mention} why you gotta cause',
                'I\'m fuming'
                'welp',
                'I blame you',
                'don\'t tell Nick but',
                'keep this one under wraps but',
                ':triumph:'
            )
            await ctx.send(f"{f'{choice(error_flairs)}, a' if randint(0,1) else 'A'}n error occured: `{error.__class__.__name__}: {error}`")

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


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
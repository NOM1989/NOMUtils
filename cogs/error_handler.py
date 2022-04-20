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
from cogs.utils.utils import get_cmd_usage

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.error_emoji = self.bot.config['emojis']['error']

    def add_extra(self, ctx):
        return f' {ctx.error_extra}' if ctx.error_extra else ''

    def add_usage(self, ctx):
        cmd_usage = get_cmd_usage(ctx)
        return f' - `{cmd_usage}`' if cmd_usage else ''

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """

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
        if hasattr(ctx, 'error_handled') and ctx.error_handled:
            return
        ctx.error_extra = getattr(ctx, 'error_extra', None)

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
            text = f"{ctx.bot.config['emojis']['error']}{self.add_extra(ctx)}{self.add_usage(ctx)}"
            await ctx.reply(text, allowed_mentions=discord.AllowedMentions.none())
            # await ctx.send(f"`{error.__class__.__name__}` - \'**{error.param}**\'{str(error).strip(str(error.param))}")
        
        elif isinstance(error, commands.BadUnionArgument) and error.param.name == 'who': #Used when converting to a discord member or user Object
            await ctx.reply(f"{self.error_emoji} Sorry, I couldn't recognise that user{self.add_extra(ctx)}", allowed_mentions=discord.AllowedMentions.none())
            # Add any additional error info I want displayed to ctx.error_extra = error_extra - see public.py for eg

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
                'pop',
                'sorry',
                '<@421362214558105611> pls fix',
                'Someone fix this',
                'smh',
                'this wasnt expected',
                ':shushing_face:',
                'rip',
                'why you gotta cause',
                'I\'m fuming'
                'welp',
                'I blame you',
                'keep it under wraps but',
                ':triumph:'
            )
            await ctx.reply(f"{self.error_emoji} {f'{choice(error_flairs)}, a' if randint(0,1) else 'A'}n error occured: `{error.__class__.__name__}: {error}`", allowed_mentions=discord.AllowedMentions.none())

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
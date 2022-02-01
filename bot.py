from dotenv import load_dotenv
load_dotenv()
import discord
from discord.ext import commands
from os import getenv
import traceback
import sys
# from asyncio import sleep
import asyncpg

extensions = (
    'cogs.owner',
    'cogs.error_handler',
    'cogs.admin',
    'cogs.tools',
    'cogs.starboard',
    'cogs.poofboard',
    'cogs.summary',
    'cogs.auto',
    'cogs.minecraft',
    'cogs.rubber',
    'cogs.public')
# extensions = ('cogs.owner', 'cogs.error_handler', 'cogs.public')

class NOMUtils(commands.Bot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions(everyone=False) #allowed_mentions makes it so not able to @everyone ever (globally)
        # Intents initialisation
        intents = discord.Intents.default()
        intents.typing = False
        intents.presences = False
        intents.members = True
        super().__init__(
            command_prefix=["?"],
            # command_prefix=["e!"],
            description='NOM#7666\'s Utility bot',
            owner_id=421362214558105611,
            allowed_mentions=discord.AllowedMentions(everyone=False),
            case_insensitive=True,
            help_command=None,
            intents=intents
        )

        self.config = {
            'emojis': {
                'error': '<:error:938203108012605470>'
            }
        }

bot = NOMUtils()
bot.remove_command('help')

@bot.event
async def on_ready():
    print('NOMUtils is ready.')
    # await sleep(3)
    # await bot.change_presence(status=discord.Status.invisible)

debug_mode = False #wether or not to connect to the db
token = getenv('BOT_TOKEN')
db_username = getenv('DB_USERNAME')
db_pass = getenv('DB_PASS')
db_name = getenv('DB_NAME')
db_host = getenv('DB_HOST')
if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()
    try:
        # NOTE: 127.0.0.1 is the loopback address. If db is running on the same machine as the code, this address will work
        if not debug_mode:
            credentials = {"user": db_username, "password": db_pass, "database": db_name, "host": db_host}
            bot.pool = bot.loop.run_until_complete(asyncpg.create_pool(**credentials))
        bot.loop.run_until_complete(bot.start(token))
    except KeyboardInterrupt:
        # cancel all tasks lingering
        if not debug_mode:
            bot.loop.run_until_complete(bot.pool.close())
        bot.loop.run_until_complete(bot.close())
    finally:
        bot.loop.close()
from dotenv import load_dotenv
load_dotenv()

from cogs.utils.context import Context
from discord.ext import commands
from os import getenv
import traceback
import discord
import asyncpg
import sys

# from cogs.utils.cache import GuildInfo

extensions = (
    'cogs.admin',
    'cogs.auto',
    'cogs.error_handler',
    'cogs.owner',
    'cogs.poofboard',
    'cogs.public',
    'cogs.rubber',
    'cogs.starboard',
    'cogs.summary',
    'cogs.tools',
    'cogs.trolling',
    'cogs.wordcloud')
# extensions = ('cogs.owner', 'cogs.error_handler', 'cogs.wordcloud')

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
                'error': '<:error:938203108012605470>',
                'green': '<:green:943119597144518676>'
            },
            'keys': {}
        }

        # self.pool: asyncpg.Pool = None

        # self.cache: dict[int, GuildInfo] = {}
        # self.load_keys()
    
    # async def ensure_cache(self, pool: asyncpg.Pool, guild_id):
    #     if str(guild_id) not in self.cache:
    #         self.cache[str(guild_id)] = GuildInfo(guild_id, pool)

    # Replace default context with my custom one
    async def get_context(self, message, *, cls=Context):
        return await super().get_context(message, cls=cls)

bot = NOMUtils()

@bot.event
async def on_ready():
    print('NOMUtils is ready.')

debug_mode = False #whether or not to connect to the db (True means dont connect)
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
            credentials = {"user": getenv('DB_USERNAME'), "password": getenv('DB_PASS'), "database": getenv('DB_NAME'), "host": getenv('DB_HOST')}
            bot.pool = bot.loop.run_until_complete(asyncpg.create_pool(**credentials))
        bot.loop.run_until_complete(bot.start(getenv('BOT_TOKEN')))
    except KeyboardInterrupt:
        # cancel all tasks lingering
        if not debug_mode:
            bot.loop.run_until_complete(bot.pool.close())
        bot.loop.run_until_complete(bot.close())
    finally:
        bot.loop.close()
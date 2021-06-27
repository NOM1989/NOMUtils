from dotenv import load_dotenv
load_dotenv()
import discord
from discord.ext import commands
import os
# import asyncpg

extensions = ('cogs.admin', 'cogs.tools', 'cogs.events', 'cogs.summary')

# Intents initialisation
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True

bot = commands.Bot(
    command_prefix=["?"],
    # command_prefix=["e!"],
    description='NOM#7666\'s Utility bot',
    owner_id=421362214558105611,
    allowed_mentions=discord.AllowedMentions(everyone=False),
    case_insensitive=True,
    help_command=None,
    intents=intents
) #allowed_mentions makes it so not able to @everyone ever (globally)

bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='poggers'))
    print('NOMUtils is ready.')

token = os.getenv('BOT_TOKEN')
# db_username = os.getenv('DB_USERNAME')
# db_pass = os.getenv('DB_PASS')
# db_name = os.getenv('DB_NAME')
# db_host = os.getenv('DB_HOST')
if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as error:
            print('{} cannot be loaded. [{}]'.format(extension, error))
    try:
        # NOTE: 127.0.0.1 is the loopback address. If db is running on the same machine as the code, this address will work
        # credentials = {"user": db_username, "password": db_pass, "database": db_name, "host": db_host}
        # bot.db = bot.loop.run_until_complete(asyncpg.create_pool(**credentials))
        bot.loop.run_until_complete(bot.start(token))
    except KeyboardInterrupt:
        # cancel all tasks lingering
        # bot.loop.run_until_complete(bot.db.close())
        bot.loop.run_until_complete(bot.close())
    finally:
        bot.loop.close()
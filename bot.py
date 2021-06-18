from dotenv import load_dotenv
load_dotenv()
import discord
from discord.ext import commands
import os

extensions = ('cogs.admin', 'cogs.tools', 'cogs.summary')

# Intents initialisation
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True

bot = commands.Bot(
    command_prefix=["?"],
    # command_prefix=["e!"],
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
if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as error:
            print('{} cannot be loaded. [{}]'.format(extension, error))

    bot.run(token)
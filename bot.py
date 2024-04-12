from cogs.utils.context import Context
from discord.ext import commands
import traceback
import asyncpg
import discord
import sys

# from cogs.utils.cache import GuildInfo

# extensions = (
#     "cogs.admin",
#     "cogs.auto",
#     "cogs.error_handler",
#     "cogs.owner",
#     "cogs.poofboard",
#     "cogs.public",
#     "cogs.rubber",
#     "cogs.starboard",
#     "cogs.summary",
#     "cogs.tools",
#     "cogs.trolling",
#     "cogs.wordcloud",
# )
extensions = (
    "cogs.owner",
    "cogs.error_handler",
)

# wordcloud, admin, public, trolling, roles, public_apis, tools


class MyEmojis:
    """Class to represent custom emojis the bot makes use of"""

    def __init__(self) -> None:
        self.error = "<:ers_error:1113498344736694403>"
        self.check = "<:ers_check:1113497881991712809>"
        self.question = "<:ers_question:1113497012025962507>"
        self.typing = "<a:typing:931524283065319446>"


class NOMUtils(commands.Bot):
    """Custom bot context"""

    def __init__(self):
        # Intents initialisation
        intents = discord.Intents.default()
        intents.typing = False
        intents.presences = False
        intents.members = True
        intents.message_content = True
        super().__init__(
            # command_prefix=["?"],
            command_prefix=["e!"],
            description="NOM#7666's Utility bot",
            owner_id=421362214558105611,
            allowed_mentions=discord.AllowedMentions(
                everyone=False
            ),  # allowed_mentions makes it so not able to @everyone ever (globally)
            case_insensitive=True,
            help_command=None,
            intents=intents,
        )

        self.my_emojis = MyEmojis()  # Custom emojis used through out the bot

        self.pool: asyncpg.Pool = None  # type: ignore

        # self.cache: dict[int, GuildInfo] = {}
        # self.load_keys()

    # async def ensure_cache(self, pool: asyncpg.Pool, guild_id):
    #     if str(guild_id) not in self.cache:
    #         self.cache[str(guild_id)] = GuildInfo(guild_id, pool)

    # Replace default context with my custom one
    async def get_context(self, message, *, cls=Context):
        return await super().get_context(message, cls=cls)

    async def setup_hook(self):
        for extension in extensions:
            try:
                await self.load_extension(extension)
            except Exception as e:
                print(f"Failed to load extension {extension}.", file=sys.stderr)
                traceback.print_exc()

    async def on_ready(self):
        print("NOMUtils is ready.")

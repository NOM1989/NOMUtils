from datetime import datetime
from discord.ext import commands
from discord.utils import format_dt
from bot import NOMUtils
from .utils.context import Context
from random import randint
from discord import AllowedMentions, Embed, Member, TextChannel, Thread


class Discovered:
    def __init__(self) -> None:
        self.user = "discovery_user"
        self.timestamp = "discovery_timestamp"


class AbstractCelestial:
    def __init__(
        self,
        name: str,
        description: str,
        discovered: Discovered,
        thread: Thread | None = None,
        visits: int = 0,
        last_visit: int | None = None,
        image_uri: str | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.discovered = discovered
        self.thread = thread
        self.visits = visits
        self.last_visit = last_visit
        self.image_uri = image_uri

    async def setup_thread(self, channel: TextChannel) -> None:
        """Creates a thread for the celestial and sends the related info embed in Discord"""
        # embed = Embed(title=self.name, description=self.description)
        embed = Embed()
        embed.add_field(
            name="First discovered",
            value=f"by {self.discovered.user} {self.discovered.timestamp}",
        )
        embed.add_field(name="Visits", value=self.visits)
        embed.add_field(name="Last Visit", value=format_dt(datetime.now()))
        self.thread = await channel.create_thread(name=self.name, invitable=False)
        # TODO: Experiment with image above or below title and description
        await self.thread.send(f"## {self.name}\n {self.description}", embed=embed)

    async def add_user(self, user: Member):
        await self.thread.add_user(user)

    async def remove_user(self, user: Member):
        await self.thread.remove_user(user)


class Planet(AbstractCelestial):
    def __init__(
        self,
        name: str,
        description: str,
        discovered: Discovered,
        thread: Thread | None = None,
        visits: int = 0,
        last_visit: int | None = None,
    ) -> None:
        super().__init__(name, description, discovered, thread, visits, last_visit)


class System(AbstractCelestial):
    def __init__(
        self,
        name: str,
        description: str,
        discovered: Discovered,
        planets: list[Planet],
        thread: Thread | None = None,
        radio_thread: Thread | None = None,
        visits: int = 0,
        last_visit: int | None = None,
    ) -> None:
        super().__init__(name, description, discovered, thread, visits, last_visit)
        self.radio_thread = radio_thread
        self.planets = planets

    async def setup_radio_thread(self, channel: TextChannel):
        """Creates the radio thread for the system"""
        self.radio_thread = await channel.create_thread(name=self.name, invitable=False)

    async def create_system_threads(
        self, nav_channel: TextChannel, radio_channel: TextChannel
    ):
        """Creates the relevant threads in Discord for the system, planets and radio"""
        for planet in self.planets:
            await planet.setup_thread(nav_channel)
        await self.setup_thread(nav_channel)
        await self.setup_radio_thread(radio_channel)

    async def add_user(self, user: Member):
        """Add user to all the relevant system, planet and radio threads"""
        await self.thread.add_user(user)
        for planet in self.planets:
            await planet.add_user(user)

        # Add to system radio thread
        await self.radio_thread.send(f":rocket: {user.mention} just entered the system")

    async def remove_user(self, user: Member):
        """Remove user from all the relevant system, planet and radio threads"""
        for planet in self.planets:
            await planet.remove_user(user)
        await self.thread.remove_user(user)

        # Remove from system radio thread
        await self.radio_thread.remove_user(user)
        await self.radio_thread.send(
            f":rocket: {user.mention} just left the system",
            allowed_mentions=AllowedMentions.none(),
        )


class SpaceGame:
    """Class that wraps up the game to not interfere with existing attrs of Member, each player will have an instance of this"""

    def __init__(self, system: System, planet: Planet | None = None) -> None:
        self.system = system
        self.planet = planet


# class Player(Member):
#     """Extended version of member (use the same thing as custom context to implement this)"""
#
#     def __init__(
#         self,
#         system: System,
#         planet: Planet | None = None,
#         *,
#         data: MemberWithUserPayload,  # type: ignore
#         guild: Guild,
#         state: ConnectionState,
#     ):
#         super().__init__(data=data, guild=guild, state=state)
#         self.spacegame = SpaceGame(system, planet)


# class Database:


class SpaceGameCog(commands.Cog):
    def __init__(self, bot: NOMUtils):
        self.bot: NOMUtils = bot
        self.spacegame_guild_id = 1228373936601960463
        self.nav_channel: TextChannel
        self.radio_channel: TextChannel

    async def cog_load(self):
        """Initialises the floor category on load"""
        self.nav_channel = await self.bot.fetch_channel(1228384447762530374)  # type: ignore
        self.radio_channel = await self.bot.fetch_channel(1228394449508372651)  # type: ignore

    def cog_check(self, ctx):
        return ctx.guild.id == self.spacegame_guild_id
        # return ctx.guild is not None and ctx.guild.id == self.spacegame_guild_id

    # async def cog_before_invoke(self, ctx: Context) -> None:
    #     ctx.spacegame = SpaceGame()

    async def generate_planet(self, parsed_planets: list[str]):
        return Planet(parsed_planets[0], parsed_planets[1], Discovered())

    async def generate_system(self):
        # planet_count = randint(0, 3) + randint(0, 4)
        planet_count = 1
        gpt_res_name = "System_Name"
        gpt_res_desc = "System_Description"
        parsed_planets = [["planet_name", "planet_desc"] * planet_count]

        # Create the system and planet objects
        system = System(
            gpt_res_name,
            gpt_res_desc,
            Discovered(),
            [
                await self.generate_planet(parsed_planets[i])
                for i in range(planet_count)
            ],
        )

        # Create the threads for them in Discord
        await system.create_system_threads(self.nav_channel, self.radio_channel)

        return system

    @commands.guild_only()
    @commands.command()
    async def space_test(self, ctx: Context):
        """Jump a user to another system"""
        player: Member = ctx.author  # type: ignore - Cog check limits this to guild only

        system = await self.generate_system()

        # And add the player to it
        await system.add_user(player)

    @commands.guild_only()
    @commands.command()
    async def jump(self, ctx: Context):
        """Jump a user to another system"""
        ctx.spacegame = SpaceGame(await self.generate_system())
        player: Member = ctx.author  # type: ignore - Cog check limits this to guild only
        if randint(1, 3) == 1:
            # Visit a pre-existing System
            pass
        else:
            # Visit a new System
            # First leave the current one
            await ctx.spacegame.system.remove_user(player)

            # Then generate a new one
            # Generation time for the system can be thought of as the 'travel time'
            system = await self.generate_system()

            # And add the player to it
            await system.add_user(player)


async def setup(bot):
    await bot.add_cog(SpaceGameCog(bot))


# TODO: Consider making larger GPT queries and caching the response to then dissect later eg. generate 10 planets rather than generate a planet
# TODO: Look into @overload for generating new system
# TODO: Look into ThreadWithMessage
# NB: system id is its name, and planet id is system name + planet name


# TODO: look into extending the Member class with the Player class, maybe converters will help?

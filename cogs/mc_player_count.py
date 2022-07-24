from discord.ext import tasks, commands
from mcstatus import MinecraftServer
from bot import NOMUtils
import discord

class MCPlayerCount(commands.Cog):
    def __init__(self, bot):
        self.bot: NOMUtils = bot
        self.server = MinecraftServer('51.89.194.163', 25599)
        self.indicator_guild_id = 1000765335630250004
        self.indicator_guild: discord.Guild = None #Fetched later
        self.players_online: int = None
        self.ping_server.start()

    async def update_indicator_guild(self):
        """The indicator is a server and we update the name of it to show the number of players"""
        await self.indicator_guild.edit(name=str(self.players_online).ljust(2, '0'))
        # print('updated server name')

    @tasks.loop(minutes=5)
    async def ping_server(self):
        """Ping the MC server for player count and call relevant actions"""
        # print('Pinged server!')
        status = self.server.status()
        if status.players.online != self.players_online:
            self.players_online = status.players.online
            await self.update_indicator_guild()

    @ping_server.before_loop
    async def before_ping_server(self):
        """Wait till bot is ready before starting loop"""
        await self.bot.wait_until_ready()
        self.indicator_guild = self.bot.get_guild(self.indicator_guild_id)

def setup(bot):
    bot.add_cog(MCPlayerCount(bot))
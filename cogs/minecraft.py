from discord import player
from discord.ext import commands
import discord
from mcstatus import MinecraftServer
# from json import dumps as json_dumps
import socket

class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server = MinecraftServer("54.37.169.244", 25583) #25583 54.37.169.244:25565

    async def cog_check(self, ctx):
        if (ctx.guild and ctx.guild.id == 593542699081269248) or await self.bot.is_owner(ctx.author): #ROG
        # if ctx.guild and ctx.guild.id == 776206487395631145: #Test Server
            return True
        else:
            return False

    @commands.group(aliases=['minecraft'])
    async def mc(self, ctx):
        async with ctx.typing():
            try:
                ping = self.server.ping()
                query_res = self.server.query()
                mc_embed = discord.Embed(colour = 0x27ab3f, description=f'**{query_res.players.online}/{query_res.players.max}** players online')
                mc_embed.set_author(name='MC Status', icon_url='https://freepngimg.com/thumb/minecraft/80501-biome-square-pocket-edition-grass-minecraft-block.png')
                if query_res.players.names:
                    mc_embed.add_field(name='Players', value='\n'.join(query_res.players.names))
                mc_embed.set_footer(text=f'Ping: {ping}ms')
            except socket.timeout:
                mc_embed = discord.Embed(colour=discord.Colour.red(), description=f'Server did not respond!')
                mc_embed.set_author(name='MC Status', icon_url='https://static.wikia.nocookie.net/minecraft/images/3/3b/SkullNew.png/revision/latest/scale-to-width-down/250?cb=20190901190110')
                mc_embed.set_footer(text='It\'s probably dead :/')

        await ctx.send(embed=mc_embed, delete_after=120)


    '''
    @mc.command()
    async def online(self, ctx):
        # 'status' is supported by all Minecraft servers that are version 1.7 or higher.
        status = self.server.status()
        await ctx.send(f"The server has {status.players.online} players and replied in {status.latency} ms")

        # # 'ping' is supported by all Minecraft servers that are version 1.7 or higher.
        # # It is included in a 'status' call, but is exposed separate if you do not require the additional info.
        # latency = self.server.ping()
        # print(f"The server replied in {latency} ms")

        # 'query' has to be enabled in a servers' server.properties file.
        # It may give more information than a ping, such as a full player list or mod information.
        query = self.server.query()
        # print(query)
        # print(query.players)
        # print(query.players.names)
        await ctx.send(f"The server has the following players online: {', '.join(query.players.names)}")



        """
        Prints server status and query in json. Supported by all Minecraft
        servers that are version 1.7 or higher.
        """
        data = {}
        data["online"] = False
        # Build data with responses and quit on exception
        try:
            ping_res = self.server.ping()
            data["online"] = True
            data["ping"] = ping_res

            status_res = self.server.status(tries=1)
            data["version"] = status_res.version.name
            data["protocol"] = status_res.version.protocol
            data["motd"] = status_res.description
            data["player_count"] = status_res.players.online
            data["player_max"] = status_res.players.max
            data["players"] = []
            if status_res.players.sample is not None:
                data["players"] = [{"name": player.name, "id": player.id} for player in status_res.players.sample]

            query_res = self.server.query(tries=1)
            data["host_ip"] = query_res.raw["hostip"]
            data["host_port"] = query_res.raw["hostport"]
            data["map"] = query_res.map
            data["plugins"] = query_res.software.plugins
        except:
            pass
        print(json_dumps(data))
    '''

    '''
    async def _get_player_list(self):
        # Prioraise this check then if unrecognised player do the deeper one
        query_res = self.server.query(tries=1)
        
        unknown_players = set(query_res.players.names) - self.known_players_set # Gives a list of player names who are online that are not currently in the db/the name cannot be found in the db

        if unknown_players:
            # Attempt to ressolve unknown name
            # -> either it is a new player (not in the db)
            # -> or a current player changed their name
            status_res = self.server.status(tries=1) # This request gets player name and id (id will be the same after name change)
            if status_res.players.sample is not None:
                for player in status_res.players.sample:
                    if player.id != '000-000-000':
                        if player.name not in unknown_players: #Players who chose to stay anonymous will not be checked (hopefully)
                            con = self.bot.pool
                            # Check for name change and if its changed update db to hold new name
                            query = """UPDATE user_map x
                                        SET minecraft_name = $1
                                        FROM (SELECT minecraft_id, minecraft_name FROM user_map WHERE minecraft_id = $2 FOR UPDATE) y 
                                        WHERE x.minecraft_id = y.minecraft_id
                                        RETURNING y.minecraft_name;"""
                            possible_old_name = await con.execute(query, player.name, player.id)

                            if possible_old_name: # Name was changed and has now been updated
                                self.known_players_set.remove(possible_old_name)
                                self.known_players_set.add(player.name)
                            else: # mc_ID was not found --> player not in DB
                                # Add them if we have the data --> add new player to DB and ping NOM to add extra info
                                query = """INSERT INTO user_map(minecraft_name, minecraft_id)
                                            VALUES ($1, $2);"""
                            await con.execute(query, player.name, player.id)                        



    async def check(self, ctx):
        



        # for player check if anyone wants them
    '''

def setup(bot):
    bot.add_cog(Minecraft(bot))
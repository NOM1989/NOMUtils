from utils import read_data, write_data
from discord.ext import commands
from mcstatus import MinecraftServer
# from json import dumps as json_dumps
from datetime import datetime
import discord
import socket
import json
import re

with open('options.json') as x:
    options = json.load(x)

#Ensure data is present for later
if 'minecraft' not in options:
    options['minecraft'] = {
        'ip': "0.0.0.0",
        'port': 0
    }
    with open(f'options.json', 'w') as x:
        json.dump(options, x, indent=2)
###

class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ip_and_port = [options['minecraft']['ip'], options['minecraft']['port']]
        self.server = MinecraftServer(self.ip_and_port[0], self.ip_and_port[1]) #listening port on server must be set as the same as port on end of ip

    async def cog_check(self, ctx):
        # if ctx.guild and ctx.guild.id == 776206487395631145: #Test Server
        return (ctx.guild and ctx.guild.id == 593542699081269248) or isinstance(ctx.channel, discord.DMChannel) or await self.bot.is_owner(ctx.author) #ROG

    async def get_mc_embed(self, timestamp, bypass_min=False):
        try:
            ping = self.server.ping()
            query_res = self.server.query()
            mc_embed = discord.Embed(colour = 0x27ab3f, description=f'**{query_res.players.online}/{query_res.players.max}** players online', timestamp=timestamp)
            mc_embed.set_author(name='MC Status', icon_url='https://freepngimg.com/thumb/minecraft/80501-biome-square-pocket-edition-grass-minecraft-block.png')
            if query_res.players.names and (len(query_res.players.names) > 2 or bypass_min):
                mc_embed.add_field(name='Players', value='\n'.join(query_res.players.names))
            mc_embed.set_footer(text=f'Ping: {round(ping)}ms')
        except (socket.timeout, OSError, ConnectionResetError, ConnectionRefusedError) as e:
            mc_embed = discord.Embed(colour=discord.Colour.red(), description=f'Server did not respond!\nError: `{e.__class__.__name__}: {e}`', timestamp=timestamp)
            mc_embed.set_author(name='MC Status', icon_url='https://static.wikia.nocookie.net/minecraft/images/3/3b/SkullNew.png/revision/latest/scale-to-width-down/250?cb=20190901190110')
            mc_embed.set_footer(text=f"{'Has IP changed?' if e is ConnectionRefusedError else ''}")
        return mc_embed

    @commands.group(aliases=['mc'], invoke_without_command=True)
    async def minecraft(self, ctx):
        async with ctx.typing():
            mc_embed = await self.get_mc_embed(ctx.message.created_at, True if ctx.message.author.id == self.bot.owner_id else False)
        msg = await ctx.send(embed=mc_embed)
        await msg.add_reaction('🔄')

    async def adress_to_show(self, ctx): #Hide the ip incase of command misuse (in non trusted server)
        if ctx.guild and ctx.guild.id not in (593542699081269248, 776206487395631145):
            return '`[REDACTED]`'
        return f'`{self.ip_and_port[0]}:{self.ip_and_port[1]}`'

    @commands.is_owner()
    @minecraft.command(aliases=['ip_port', 'address'])
    async def ip(self, ctx, new_ip_and_port=None):
        """Change the ip (and port) the command querys"""
        if new_ip_and_port:
            # Could have made the pattern myself but: ( + https://ihateregex.io/expr/ip/ + ): + https://ihateregex.io/expr/port/
            pattern = r'^((\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}):((6553[0-5])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-5]{0,5})|([0-9]{1,4}))$'
            # Note - could re.compile to save on processing but: "The compiled versions of the most recent
            # patterns passed to re.compile() and the module-level matching functions are cached, so programs
            # that use only a few regular expressions at a time needn’t worry about compiling regular expressions." ~ docs
            match = re.fullmatch(pattern, new_ip_and_port)
            if match:
                ip_and_port = [match.group(1), int(match.group(5))]
                if self.ip_and_port != ip_and_port:
                    self.ip_and_port = [match.group(1), int(match.group(5))]
                    self.server = MinecraftServer(self.ip_and_port[0], self.ip_and_port[1])
                    options = await read_data('options')
                    options['minecraft']['ip'] = self.ip_and_port[0]
                    options['minecraft']['port'] = self.ip_and_port[1]
                    await write_data('options', options)
                    await ctx.reply(f"Set address to: `{self.ip_and_port[0]}:{self.ip_and_port[1]}`")
                else:
                    await ctx.reply(f'Address already set to: `{self.ip_and_port[0]}:{self.ip_and_port[1]}`')
            else:
                await ctx.reply('Sorry, address invalid - format example: `192.168.1.1:8080`')
        else:
            await ctx.reply(f'Current address is set to: {await self.adress_to_show(ctx)}')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        message = reaction.message
        if message.author == self.bot.user and reaction.emoji == '🔄' and not user.bot and message.embeds and message.embeds[0].author.name == 'MC Status':
            await message.add_reaction('<a:typing:931524283065319446>')
            mc_embed = await self.get_mc_embed(datetime.utcnow())
            await message.edit(embed=mc_embed)
            await message.remove_reaction('<a:typing:931524283065319446>', message.author) #message.author is the bot
            try:
                await reaction.remove(user)
            except discord.errors.Forbidden: #In the case of DM usage
                pass
        return

    '''
    @minecraft.command()
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
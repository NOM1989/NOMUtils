from discord.ext import commands
from bot import NOMUtils
import discord

class Trolling(commands.Cog):
    def __init__(self, bot):
        self.bot: NOMUtils = bot
        self.exempt_guilds: list[int] = [749665566884757566]
        self.exempt_members: list[int] = [405764666531381248]
        self.tmp_name_store: dict[int, str] = {}

        self.NO_VIEWERS_NAME: str = 'no viewers?'

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.TextChannel):
        """Sends 'first' in a newly created channel"""
        if channel.guild.id not in self.exempt_guilds and isinstance(channel, discord.TextChannel):
            await channel.send('first')

    async def _set_nickname(self, member: discord.Member, overwrite=False):
        """Sets a users nickname for no stream viewers"""
        name = member.display_name #Incase of error?
        if overwrite:
            name = self.NO_VIEWERS_NAME
            self.tmp_name_store[member.id] = member.display_name
        else:
            name = self.tmp_name_store[member.id]
            try:
                del self.tmp_name_store[member.id]
            except KeyError: #User's origional name was self.NO_VIEWERS_NAME
                pass

        try:
            await member.edit(nick=name)
        except discord.Forbidden:
            # print(f'Forbidden to edit {member.name}[{member.id}]')
            pass
        
        # print(f'Set {member}\'s name to: {name}')
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Sets a user's name to self.NO_VIEWERS_NAME if no one is watching their stream"""
        if member.guild.id not in self.exempt_guilds and member.id not in self.exempt_members:
            # print('Voice state update! - ', member, before.channel, after.channel, len(getattr(after.channel, 'members', [])))
            # print(member.name, len(after.channel.members) > 1)

            # Filters for only leave/join events
            if before.channel != after.channel:
                # Account for user leaving someone to stream alone
                if before.channel and len(before.channel.members) == 1 and before.channel.members[0].voice.self_stream:
                    await self._set_nickname(before.channel.members[0], overwrite=True) #no views

                # Account for someone joining lonely stream
                if after.channel and len(after.channel.members) == 2:
                    for channel_member in after.channel.members:
                        if channel_member != member and channel_member.id in self.tmp_name_store:
                            await self._set_nickname(channel_member) #origional
            
            # Account for stop stream or leave vc
            if member.id in self.tmp_name_store and ((before.self_stream == True and after.self_stream == False) or after.channel == None):
                await self._set_nickname(member) #origional

            # Account for start stream
            elif after.channel and after.self_stream and len(after.channel.members) == 1 and member.id not in self.tmp_name_store:
                await self._set_nickname(member, overwrite=True) #no views


async def setup(bot):
    await bot.add_cog(Trolling(bot))

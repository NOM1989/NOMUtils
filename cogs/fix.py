from cogs.utils.utils import get_webook
from discord.ext import commands
from asyncio import sleep
from bot import NOMUtils
import discord

class Fix(commands.Cog):
    def __init__(self, bot):
        self.bot: NOMUtils = bot
        self.sleep_time = 0.5

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    def base_embed(self, text: str, footer: str = None):
        if not footer:
            footer = discord.Embed.Empty
        embed = discord.Embed(description=text, color=discord.Colour.dark_purple())
        embed.set_footer(text=footer)
        return embed

    async def prepare(self, ctx: commands.Context):
        '''Maps all channels with a 2 at the end to the version of the channel without'''
        channels: dict[str, discord.TextChannel] = {}
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                channels[channel.name] = channel
        
        channel_map: dict[str, discord.TextChannel] = {}
        for channel_name in channels.keys():
            alt_name = f'{channel_name}-2'
            if alt_name in channels:
                channel_map[alt_name] = channels[channel_name]
        
        if channel_map:
            embed = discord.Embed(title='Migration Assistant', description=f'**{len(channel_map)} channels** have been mapped to their counterpart!', color=discord.Colour.purple())
            await ctx.reply(embed=embed)
        else:
            await ctx.reply('No channels to migrate!')
        return channel_map, channels

    async def forward_messages(self, from_channel: discord.TextChannel, to_channel: discord.TextChannel):
        '''Forward all messages in `from_channel` to `to_channel`'''
        webhook = await get_webook(self.bot, to_channel)
        async for message in from_channel.history(limit=None, oldest_first=True):
            files = []
            if message.attachments:
                for attachment in message.attachments:
                    files.append(await attachment.to_file())
            await webhook.send(content=((message.content[:1972] + '..') if len(message.content) > 1974 else message.content), files=files, embeds=message.embeds, username=message.author.display_name, avatar_url=message.author.display_avatar.url, allowed_mentions=discord.AllowedMentions.none())
            await sleep(self.sleep_time)
    
    async def copy_perms(self, from_channel: discord.TextChannel, to_channel: discord.TextChannel):
        '''Copies the permissions from `from_channel` to `to_channel`'''
        for overwrite in from_channel.overwrites:
            await to_channel.set_permissions(overwrite, overwrite=from_channel.overwrites[overwrite])

    async def migration_function(self, ctx, from_channel: discord.TextChannel, to_channel: discord.TextChannel, copy_perms:bool = False):
        '''Migrate `from_channel` to `to_channel`, deleting the `from_channel`'''
        msg: discord.Message = await ctx.send(embed=self.base_embed(f'Migrate {from_channel.mention} --> {to_channel.mention}?', footer='Copying permissions' if copy_perms else None))
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')

        def check(reaction, user):
            return user == ctx.message.author and \
                str(reaction.emoji) in ('✅','❌')
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=30.0)
        except TimeoutError:
            await ctx.send('Took too long, `aborting`')
            return
        else:
            if reaction.emoji == '❌':
                await msg.edit(embed=self.base_embed(f':x: Did not migrate {from_channel.mention} --> {to_channel.mention}'))
            elif reaction.emoji == '✅':
                await msg.edit(embed=self.base_embed(f':arrows_counterclockwise: Migrating {from_channel.mention} --> {to_channel.mention}'))
                await self.forward_messages(from_channel, to_channel)
                extra = None
                try:
                    if copy_perms:
                        await self.copy_perms(from_channel, to_channel)
                    await from_channel.delete(reason='April Fool!')
                except:
                    extra = f"Could not {'copy perms/' if copy_perms else ''}delete: {from_channel.name}"
                await msg.edit(embed=self.base_embed(f"{self.bot.config['emojis']['green']} Migrated to {to_channel.mention}", footer=extra))
            try:
                await msg.clear_reactions()
            except discord.errors.Forbidden:
                pass

    @commands.group(invoke_without_command=True)
    async def migrate(self, ctx: commands.Context, channel: discord.TextChannel, copy_perms:bool = True):
        '''Migrate the specified `channel` to the current one, if `copy_perms` then permissions also copied'''
        await self.migration_function(ctx, channel, ctx.channel, copy_perms)

    @migrate.command(name='all')
    async def migrate_all(self, ctx, copy_perms:bool = True):
        '''Migrate all channels to their map counterpart'''
        channel_map, channels = await self.prepare(ctx)
        for channel_name in channel_map:
            await self.migration_function(ctx, channels[channel_name], channel_map[channel_name], copy_perms)

def setup(bot):
    bot.add_cog(Fix(bot))
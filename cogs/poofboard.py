from discord.ext import commands
from utils import read_data, write_data
import discord
import json
from datetime import datetime, timedelta

with open('options.json') as x:
    options = json.load(x)

class Poofboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.poofboard_guild_id = options['poofboard']['guild']
        self.poofboard_channel = None
        self.poofboard_webhook = None
        self.reactions_required = options['poofboard']['required']

    async def cog_check(self, ctx):
        if await self.bot.is_owner(ctx.author) and ctx.guild and ctx.guild.id == self.poofboard_guild_id:
            return True
        else:
            return False

    async def initialise_poofboy(self):
        if self.poofboard_channel == None:
            self.poofboard_channel = self.bot.get_channel(options['poofboard']['channel']) #poofboard channel
        if self.poofboard_webhook == None:
            # print(self.poofboard_channel)
            webhooks = await self.poofboard_channel.webhooks()
            for webhook in webhooks:
                if webhook.name == 'Poofboy':
                    self.poofboard_webhook = webhook
                    break
            if self.poofboard_webhook == None: #The required webhook could not be found, create one (THIS SHOULD ONLY HAPPEN ONCE!!)
                self.poofboard_webhook = await self.poofboard_channel.create_webhook(name='Poofboy')

    async def get_poof_count(self, reactions):
        poof_count = 0
        for reaction in reactions:
            if reaction.emoji == '🌫️':
                poof_count = reaction.count
                break
        return poof_count

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.guild_id and payload.guild_id == self.poofboard_guild_id and payload.emoji.name == '🌫️' and payload.channel_id not in options['poofboard']['ignored_channels']: #ignore the poofboard and other channels
            #Initialise the poofboy webhook if not done already
            await self.initialise_poofboy()

            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            async def poofboard_embed(message):
                async for above_message in message.channel.history(limit=1, before=message.created_at):
                    pass #Should onlu loop once (limit=1) and return he first message above the one marked for deletion
                footer_embed = discord.Embed(description=f"[jump nearby]({above_message.jump_url}) - {message.channel.mention}", colour=0x2F3136, timestamp=message.created_at)
                footer_embed.set_footer(text='Sent')
                return footer_embed

            if message.created_at > (datetime.today()-timedelta(days=7)): #prevent message from more than (about) a week ago from being removed
                poof_count = await self.get_poof_count(message.reactions)
                if poof_count == self.reactions_required-1:
                    #put a warning reaction
                    await message.add_reaction('⚠️')
                elif poof_count >= self.reactions_required:
                    embed = await poofboard_embed(message)
                    #check attachments, content, To do: embeds?, stickers
                    files = []
                    if message.attachments:
                        for attachment in message.attachments:
                            files.append(await attachment.to_file())

                    await self.poofboard_webhook.send(content=((message.content[:1972] + '..') if len(message.content) > 1974 else message.content), files=files, username=message.author.display_name, avatar_url=message.author.display_avatar.url, allowed_mentions=discord.AllowedMentions.none())
                    await self.poofboard_webhook.send(embed=embed, username=message.author.display_name, avatar_url=message.author.display_avatar.url, allowed_mentions=discord.AllowedMentions.none())

                    await message.delete()

    @commands.command(aliases=['required'])
    async def poofs(self, ctx, val: int):
        options = await read_data('options')
        options['poofboard']['required'] = val
        await write_data('options', options)
        self.reactions_required = val
        await ctx.send(f'{ctx.author.mention} set `required` to **{val}**')
        

def setup(bot):
    bot.add_cog(Poofboard(bot))
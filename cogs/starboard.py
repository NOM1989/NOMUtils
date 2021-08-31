from discord.ext import commands
from utils import read_data, write_data
import discord
from time import time
import json

with open('options.json') as x:
    options = json.load(x)

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.starboard_guild_id = options['starboard']['guild']
        self.starboard_channel = None
        self.starboard_webhook = None
        self.low_stars = options['starboard']['low_stars']
        self.high_stars = options['starboard']['high_stars']

    async def cog_check(self, ctx):
        if await self.bot.is_owner(ctx.author) and ctx.guild and ctx.guild.id == self.starboard_guild_id:
            return True
        else:
            return False

    async def initialise_starboy(self):
        if self.starboard_channel == None:
            self.starboard_channel = self.bot.get_channel(options['starboard']['channel']) #starboard channel
        if self.starboard_webhook == None:
            # print(self.starboard_channel)
            webhooks = await self.starboard_channel.webhooks()
            for webhook in webhooks:
                if webhook.name == 'Starboy':
                    self.starboard_webhook = webhook
                    break
            if self.starboard_webhook == None: #The required webhook could not be found, create one (THIS SHOULD ONLY HAPPEN ONCE!!)
                self.starboard_webhook = await self.starboard_channel.create_webhook(name='Starboy')

    async def get_star_count(self, reactions):
        star_count = 0
        for reaction in reactions:
            if reaction.emoji == '⭐':
                star_count = reaction.count
                break
        return star_count

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.guild_id and payload.guild_id == self.starboard_guild_id and payload.emoji.name == '⭐' and payload.channel_id != options['starboard']['channel']: #ignore the starboard channel
            #Initialise the starboy webhook if not done already
            await self.initialise_starboy()

            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            async def starboard_embed(message, star_count):
                header_embed = discord.Embed(description=f"{star_count} {':star:' if star_count < self.high_stars else ':star2:'} - [jump]({message.jump_url}) - {message.channel.mention}", colour=0x2F3136, timestamp=message.created_at)
                # header_embed = discord.Embed(description=f"[Jump!]({message.jump_url}) {message.channel.mention}", colour=0x2F3136)
                # header_embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
                # header_embed.add_field(name=f"{star_count} {':star:' if star_count < 8 else ':star2:'} in", value=message.channel.mention)
                header_embed.set_footer(text=f'{message.author.mention}')
                return header_embed

            star_count = await self.get_star_count(message.reactions)
            #Check if its already on the starboard
            index = f'{payload.channel_id}-{payload.message_id}'
            starboard_data = await read_data('starboard')
            if index not in starboard_data:
                if star_count >= self.low_stars:
                    #send message to starboard
                    embed = await starboard_embed(message, star_count)
                    #check attachments, content, To do: embeds?, stickers
                    files = []
                    if message.attachments:
                        for attachment in message.attachments:
                            files.append(await attachment.to_file())
                    # sent_message = await self.starboard_webhook.send(embed=embed, username=message.author.display_name, avatar_url=message.author.avatar_url, allowed_mentions=discord.AllowedMentions.none(), wait=True)
                    # await self.starboard_webhook.send(content=((message.content[:1972] + '..') if len(message.content) > 1974 else message.content), files=files, username=message.author.display_name, avatar_url=message.author.avatar_url, allowed_mentions=discord.AllowedMentions.none())
                    # sent_message = await self.starboard_webhook.send(content=((message.content[:1972] + '..') if len(message.content) > 1974 else message.content) + ('\n<:__:877568680899272724>' if not files else ''), files=files,  embed=embed, username=message.author.display_name, avatar_url=message.author.avatar_url, allowed_mentions=discord.AllowedMentions.none(), wait=True)
                    sent_message_1 = await self.starboard_webhook.send(content=((message.content[:1972] + '..') if len(message.content) > 1974 else message.content), files=files, username=message.author.display_name, avatar_url=message.author.avatar_url, allowed_mentions=discord.AllowedMentions.none(), wait=True)
                    sent_message_2 = await self.starboard_webhook.send(embed=embed, username=message.author.display_name, avatar_url=message.author.avatar_url, allowed_mentions=discord.AllowedMentions.none(), wait=True)
                    # print(sent_message)
                    starboard_data = await read_data('starboard')
                    starboard_data[index] = [int(time()), sent_message_1.id, sent_message_2.id]
                    await write_data('starboard', starboard_data)
            else:
                #Update star count
                embed = await starboard_embed(message, star_count)
                await self.starboard_webhook.edit_message(starboard_data[index][2], embed=embed)


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.guild_id and payload.guild_id == self.starboard_guild_id and payload.emoji.name == '⭐':
            #Initialise the starboy webhook if not done already
            await self.initialise_starboy()

            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            star_count = await self.get_star_count(message.reactions)

            index = f'{payload.channel_id}-{payload.message_id}'
            starboard_data = await read_data('starboard')
            if index in starboard_data and star_count < self.low_stars:
                await self.starboard_webhook.delete_message(starboard_data[index][1])
                await self.starboard_webhook.delete_message(starboard_data[index][2])
                starboard_data = await read_data('starboard')
                del starboard_data[index]
                await write_data('starboard', starboard_data)

    @commands.command()
    async def stars(self, ctx, category, val: int):
        if category in ('low', 'high'):
            if category == 'low':
                self.low_stars = val
            else:
                self.high_stars = val
            options = await read_data('options')
            options['starboard'][f'{category}_stars'] = val
            await write_data('options', options)
            await ctx.send(f'{ctx.author.mention} set `{category}_stars` to **{val}**, reload cog for change to take effect')
        else:
            await ctx.send(f'{ctx.author.mention} Syntax error - format: `stars <low/high> <val>`')
        

def setup(bot):
    bot.add_cog(Starboard(bot))
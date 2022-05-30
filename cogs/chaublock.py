from cogs.utils.utils import get_webook
from .utils.context import Context
from PIL import Image, ImageFilter
from discord.ext import commands
from bot import NOMUtils
from io import BytesIO
import asyncio
import discord

class ChauBlockUser():
    def __init__(self, res) -> None:
        self.user_id: int = res['user_id']
        self.tier: int = res['tier']

class BlockedMessage():
    def __init__(self, res) -> None:
        self.channel_id: int = res['channel_id']
        self.active_message_id: int = res['active_message_id']
        self.origional_attachment_url: str = res['origional_attachment_url']
        self.edited_attachment_url: str = res['edited_attachment_url']
        self.blocked_state: bool = res['blocked_state'] # True if blocked

class ChauBlock(commands.Cog):
    def __init__(self, bot):
        self.bot: NOMUtils = bot
        self.BLOCK_REACTION = ':chaublock:980551246303887501'
        self.STORAGE_CHANNEL_ID = 864900492290293800
        self.FILENAME = 'tmp_chaublock.jpeg'
        self.TMP_UNBLOCK_TIME = 30 # Seconds

        # List of users who post ads
        self.ad_posters: list[int] = [441365064503656479, 331462078546182154]
        # Protected Guils (guilds to block ads on)
        self.ad_guilds: list[int] = [593542699081269248]

        # Messages we are monitoring for block events
        self.blocked_messages: dict[int, list[int]] = {}

    async def cog_check(self, ctx: Context):
        return await self.bot.is_owner(ctx.author)

    def _add_block_message_to_local(self, channel_id, active_message_id):
        """Adds a message to self.blocked_messages"""
        if channel_id not in self.blocked_messages:
            self.blocked_messages[channel_id] = []
        self.blocked_messages[channel_id].append(active_message_id)

    async def _load_block_messages(self):
        """Loads all block messages from the db into self.blocked_messages"""
        query = """SELECT channel_id, active_message_id FROM chaublock_content;"""
        res = await self.bot.pool.fetch(query)
        for record in res:
            self._add_block_message_to_local(record['channel_id'], record['active_message_id'])

    async def _add_block_message_to_db(self, active_message: discord.WebhookMessage, origional_attachment_message_url, edited_attachment_url):
        self._add_block_message_to_local(active_message.channel.id, active_message.id)
        query = """INSERT INTO chaublock_content
            VALUES ($1, $2, $3, $4);"""

        await self.bot.pool.execute(query, active_message.channel.id, active_message.id, origional_attachment_message_url, edited_attachment_url)

    async def _generate_first_frame(self, url):
        """Generates an image of the first frame of the video, using ffmpeg"""
        # Extract the first frame from a video
        args = ['ffmpeg', '-y', '-i', url, '-r', '1', '-frames:v', '1', '-f', 'image2', self.FILENAME]
        proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.DEVNULL)
        await proc.communicate()

    def _create_image(self):
        """Create the edited (ChauBlocked) image"""
        img = Image.open(self.FILENAME).convert('L') # Base image
        img = Image.composite(
            img,
            Image.new('RGB',img.size,(51, 51, 51)), # Grey overlay
            Image.new('RGBA',img.size,(0,0,0,123)) # Transparent overaly aspect
            ).filter(ImageFilter.BLUR).filter(ImageFilter.BLUR) # Blur image

        chaublock_width = img.width*.65
        chaublock = Image.open('chaublock.png')
        chaublock = chaublock.resize(
            (
                round(chaublock_width), 
                round(chaublock_width*(chaublock.height/chaublock.width)) # Scale height proportional to width
            ),
            resample=Image.Resampling.BICUBIC
        )

        img.paste(
            chaublock,
            (
                round((img.width/2)-chaublock.width/2),
                round((img.height/2)-chaublock.height/2)
            ),
            chaublock
        )
        return img

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild.id in self.ad_guilds and message.author.id in self.ad_posters and message.attachments:
            # Only handle one as I cba to handle all
            attachment = message.attachments[0]
            content_type = attachment.content_type.split('/')[0]

            if not content_type in ('video', 'image'):
                # We cant do anything with it if its not one of these
                return

            # It begins!
            # Quickly send a message to hold the place, we edit later
            webhook = await get_webook(self.bot, message.channel)
            active_message = await webhook.send('.', username=message.author.display_name, avatar_url=message.author.display_avatar.url, wait=True)

            storage_channel = self.bot.get_channel(self.STORAGE_CHANNEL_ID)
            origional_attachment_message = await storage_channel.send(file=await message.attachments[0].to_file())
            origional_attachment_message_url = origional_attachment_message.attachments[0].url
            
            if content_type == 'video':
                await self._generate_first_frame(attachment.url)
            elif content_type == 'image':
                await attachment.save(self.FILENAME)

            # Now make use of this file and edit it
            buffer = BytesIO()
            new_image = self._create_image()
            new_image.save(buffer, 'PNG')
            buffer.seek(0)
            chaublock_image_file = discord.File(buffer, filename=f'chaublock_{attachment.filename}')
            edited_attachment_message = await storage_channel.send(file=chaublock_image_file)
            edited_attachment_url = edited_attachment_message.attachments[0].url
            buffer.close()

            # Update the placeholder message with the blocked content
            await webhook.edit_message(active_message.id, content=origional_attachment_message_url)
            await active_message.add_reaction(self.BLOCK_REACTION)
            await message.delete()

            # Add it all to local and DB
            await self._add_block_message_to_db(active_message, origional_attachment_message_url, edited_attachment_url)

    async def _fetch_blocked_message(self, channel_id, active_message_id):
        """Fetch a ChauBlocked message from the db"""
        query = """SELECT * FROM chaublock_content
            WHERE channel_id = $1 AND
            active_message_id = $2;"""
        res = await self.bot.pool.fetchrow(query, channel_id, active_message_id)
        return BlockedMessage(res)

    async def _fetch_user_info(self, user_id):
        """Fetch a (potential) ChauBlock Subscriber from the db"""
        query = """SELECT * FROM chaublock_users
            WHERE user_id = $1;"""
        res = await self.bot.pool.fetchrow(query, user_id)
        if res:
            return ChauBlockUser(res)
        return False

    async def _update_blocked_message_state(self, channel_id, active_message_id, state):
        """Update the blocked_state of a ChauBlocked message"""
        query = """UPDATE chaublock_content
            SET blocked_state = $3
            WHERE channel_id = $1 AND
            active_message_id = $2;"""
        await self.bot.pool.execute(query, channel_id, active_message_id, state)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if not payload.member.bot and payload.guild_id and payload.guild_id in self.ad_guilds and payload.emoji.name == 'chaublock' and \
        payload.channel_id in self.blocked_messages and payload.message_id in self.blocked_messages[payload.channel_id]:
            blocked_message = await self._fetch_blocked_message(payload.channel_id, payload.message_id)
            user = await self._fetch_user_info(payload.member.id)
            active_channel = await self.bot.fetch_channel(blocked_message.channel_id)
            active_message = await active_channel.fetch_message(blocked_message.active_message_id)
            # Use when updated:
            # active_message = self.bot.get_partial_messageable(blocked_message.channel_id).get_partial_message(blocked_message.active_message_id)

            if blocked_message.blocked_state:
                webhook = await get_webook(self.bot, active_channel)
                if user and user.tier == 2:
                    # Tier 2 users can toggle blocking
                    await webhook.edit_message(blocked_message.active_message_id, content=blocked_message.origional_attachment_url)
                    await active_message.remove_reaction(self.BLOCK_REACTION, payload.member)
                    await self._update_blocked_message_state(blocked_message.channel_id, blocked_message.active_message_id, False)
                else:
                    # Not privileged enough, unblock for 30 sec
                    await webhook.edit_message(blocked_message.active_message_id, content=blocked_message.origional_attachment_url)
                    await active_message.clear_reactions()
                    await asyncio.sleep(self.TMP_UNBLOCK_TIME)
                    await webhook.edit_message(blocked_message.active_message_id, content=blocked_message.edited_attachment_url)
                    await active_message.add_reaction(self.BLOCK_REACTION)
            else:
                # Block message
                if user:
                    # All users in db will be of at least teir 1 (allowed to block)
                    webhook = await get_webook(self.bot, active_channel)
                    await webhook.edit_message(blocked_message.active_message_id, content=blocked_message.edited_attachment_url)
                    await self._update_blocked_message_state(blocked_message.channel_id, blocked_message.active_message_id, True)
                await active_message.remove_reaction(self.BLOCK_REACTION, payload.member)


    @commands.group()
    async def chaublock(self, ctx: Context):
        pass

    @chaublock.command(aliases=['initialize', 'start'])
    async def initialise(self, ctx: Context):
        """Sets up the DB and loads all current subscribers"""
        con = self.bot.pool
        query = """CREATE TABLE IF NOT EXISTS chaublock_content(
            channel_id BIGINT,
            active_message_id BIGINT,
            origional_attachment_url VARCHAR,
            edited_attachment_url VARCHAR,
            blocked_state BOOLEAN DEFAULT FALSE,
            PRIMARY KEY(channel_id, active_message_id)
            );"""
        await con.execute(query)
        query = """CREATE TABLE IF NOT EXISTS chaublock_users(
            user_id BIGINT PRIMARY KEY,
            tier SMALLINT DEFAULT 1
            );"""
        await con.execute(query)
        await self._load_block_messages()
        await ctx.send('`Initialised` ChauBlock :sunglasses:')

    async def _upsert_user(self, user_id: int, tier:int = 1):
        query = """INSERT INTO chaublock_users
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE
            SET tier = $2;"""
        return await self.bot.pool.execute(query, user_id, tier)
    
    async def _remove_user(self, user_id: int):
        query = """DELETE FROM chaublock_users
            WHERE user_id = $1;"""
        return await self.bot.pool.execute(query, user_id)

    @chaublock.command()
    async def add(self, ctx: Context, member: discord.Member, tier: int = None):
        if tier == None:
            tier = 1
        tier = min(max(1, tier), 2)
        await self._upsert_user(member.id, tier)
        await ctx.reply(f'Added a **ChauBlock** `Tier {tier}` subscription to {member.mention}', allowed_mentions=discord.AllowedMentions.none())

    @chaublock.command()
    async def update(self, ctx: Context, member: discord.Member, tier: int = None):
        if tier == None:
            tier = 1
        tier = min(max(1, tier), 2)
        await self._upsert_user(member.id, tier)
        await ctx.reply(f'Updated {member.mention}\'s **ChauBlock** subscription to a `Tier {tier}`', allowed_mentions=discord.AllowedMentions.none())

    @chaublock.command()
    async def remove(self, ctx: Context, member: discord.Member):
        await self._remove_user(member.id)
        await ctx.reply(f'Removed {member.mention}\'s **ChauBlock** subscription', allowed_mentions=discord.AllowedMentions.none())

def setup(bot):
    bot.add_cog(ChauBlock(bot))
from discord.ext import tasks, commands
from utils import read_data, write_data
from random import choice, randint
from asyncio import sleep
import discord
import json

with open('options.json') as x:
    options = json.load(x)

class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_ctx = None
        self.current_vc_id = None
        self.inital_category = None
        self.tmp_role_storage = {}
        self.tmp_channel_storage = {}
        self.sec_diff_for_msgs_to_count_as_batch = 8 # Default is 8 sec
        if 'sec_diff_for_msgs_to_count_as_batch' in options:
            self.sec_diff_for_msgs_to_count_as_batch = options['sec_diff_for_msgs_to_count_as_batch']

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)
    
    def cog_unload(self):
        self.vc_evasion.cancel() #Stops the task in case of cog unload (doesnt work :/)

    @tasks.loop(seconds=2.2)
    async def vc_evasion(self):
        """The loop responsible for moving the channel when vcrun is triggered"""
        ctx = self.current_ctx
        if ctx.author.voice and ctx.author.voice.channel.id == self.current_vc_id: #User is still in a vc
            category_count = len(ctx.guild.categories)
            if category_count > 1: #This only works if there is more than one category
                target_category = ctx.author.voice.channel.category
                while target_category == ctx.author.voice.channel.category: #If you get unlucky could cause a temporary ifinate loop
                    target_category = ctx.guild.categories[randint(0, category_count-1)]
                    # print(target_category.name, ctx.author.voice.channel.category.name)
                await ctx.author.voice.channel.move(end=True, category=target_category, sync_permissions=False)
        else: #The user has left the vc
            self.vc_evasion.cancel()
            await ctx.author.voice.channel.move(end=True, category=self.inital_category, sync_permissions=False)
            self.current_ctx = None
            self.current_vc_id = None
            self.inital_category = None
            await ctx.send(f'{ctx.author.mention} :x: You left the vc, so it has stopped running')

    @commands.command(hidden=True)
    async def vcrun(self, ctx):
        """Causes the vc to move around the server"""
        #Maybe add a thing where it returns it to og pos
        if ctx.author.voice:
            if self.vc_evasion.is_running():
                self.vc_evasion.stop()
                await ctx.author.voice.channel.move(end=True, category=self.inital_category, sync_permissions=False)
                self.current_ctx = None
                self.current_vc_id = None
                self.inital_category = None
                await ctx.send(':person_standing: Your vc is no longer on the run')
            else:
                self.current_ctx = ctx
                self.current_vc_id = ctx.author.voice.channel.id
                self.inital_category = ctx.author.voice.channel.category
                self.vc_evasion.start()
                await ctx.send(':person_running: Your vc is now on the run')
        else:
            await ctx.send('You are not in vc, so it cannot run')

    @commands.command(hidden=True, aliases=['vcint'])
    async def vcinterval(self, ctx, *, new_interval):
        """Changes the interval that the vc run uses"""
        if self.vc_evasion.is_running(): #The interval is changable
            try:
                new_interval = float(new_interval)
            except:
                new_interval = False
                await ctx.send('`new_interval` was not an integer')
            if new_interval:
                new_interval = float(new_interval)
                self.vc_evasion.change_interval(seconds=new_interval)
                await ctx.send(f'Set interval to `{new_interval}`')
        else:
            await ctx.send('Your vc is not running')

    # @commands.command(hidden=True)
    # async def test(self, ctx, channel_id: int):
        # webhook = await ctx.channel.create_webhook(name='DeletedUser')
        # webhooks = await ctx.channel.webhooks()
        # print(webhooks)
        # for webhook in webhooks:
            # print(webhook.user, ctx.me.name+ctx.me.name)
            # if webhook.user == ctx.me.name:
            #     print('Using a webhook')
            # print(webhook.id) #853424812008931338
            # webhook_to_use = webhook
        # for member in ctx.channel.members:
        #     webhook = await ctx.channel.create_webhook(name='DeletedUser')
        #     if member.nick:
        #         name_to_use = member.nick
        #     else:
        #         name_to_use = member.name
        #     await webhook.send(content='Testing :)', username=name_to_use, avatar_url=member.avatar_url)
        #     await webhook.delete()
        #     await sleep(0.5)
        # channel = self.bot.get_channel(channel_id)
        # if channel:
        #     print(f'Channel: {channel}')
        # else:
        #     await ctx.send('Channel not found')

    @commands.command(hidden=True)
    async def sudo(self, ctx, member: discord.Member, *, text):
        """Impersonate a member of the server"""
        await ctx.message.delete()
        if member.nick:
            name_to_use = member.nick
        else:
            name_to_use = member.name
        webhook = await ctx.channel.create_webhook(name='DeletedUser')
        await webhook.send(content=text, username=name_to_use, avatar_url=member.avatar_url)
        await webhook.delete()
    
    @commands.command(hidden=True, aliases=['remote_sudo'])
    async def rsudo(self, ctx, member_id: int, channel_id: int,  *, text):
        """Remote sudo someone"""
        print(type(channel_id))
        channel = self.bot.get_channel(channel_id)
        if channel == None:
            await ctx.send('Channel not found')
        else:
            user = await self.bot.fetch_user(member_id)
            if user == None:
                await ctx.send('User not found')
            else:
                # find_old_webhook() - Add a way to find and use old webhooks
                webhook = await channel.create_webhook(name='DeletedUser')
                await webhook.send(content=text, username=user.name, avatar_url=user.avatar_url)
                await webhook.delete()

    @commands.command(hidden=True, aliases=['troll'])
    async def clear_roles(self, ctx, member: discord.Member):
        """Clears the targest roles (temp stores them so they can be returned later)"""
        if str(member.id) not in self.tmp_role_storage:
            origional_roles = list(member.roles)
            replace_roles = []
            for role in member.roles:
                if len(replace_roles) < 1:
                    replace_roles.append(role)
                    break
            await member.edit(roles=replace_roles)
            self.tmp_role_storage[str(member.id)] = origional_roles
            if ctx.invoked_with == 'poofers':
                reply = 'Poof! :dash:'
            else:
                reply = 'When the roles are gone :flushed:'
        else:
            reply = 'Crisis averted :sunglasses:'
        await ctx.send(reply)

    @commands.command(hidden=True, aliases=['unpoof', 'return_roles', 'untroll'])
    async def replace_roles(self, ctx, member: discord.Member):
        """Restores cleared roles"""
        if str(member.id) in self.tmp_role_storage:
            await member.edit(roles=self.tmp_role_storage[str(member.id)])
            del self.tmp_role_storage[str(member.id)]
            reply = ':fingers_crossed:'
        else:
            reply = 'Nothing to replace! :grimacing:'
            if ctx.guild.get_member(691299852352618620): #If soham is in the channel, blame him. (thats Soham Deshpande's id)
                reply = reply + ' Blame Soham.'
        await ctx.send(reply)

    @commands.command(hidden=True, aliases=['silencemedia'])
    async def silence(self, ctx, *, since_number: int = None):
        """Deletes messages starting with ? (bot prefix)"""
        if since_number == None:
            since_number = 60
        
        def is_the_media(message):
            return message.content.startswith('?') and message != ctx.message

        deleted = await ctx.channel.purge(limit=since_number, check=is_the_media)
        number_of_deleted = len(deleted)
        if number_of_deleted:
            await ctx.send(f':shushing_face: Silenced {number_of_deleted} media <:okcool:804285714312986645>')
        else:
            await ctx.message.delete()

    @commands.command(hidden=True)
    async def say(self, ctx, *, text):
        """Says what you tell it to"""
        await ctx.message.delete()
        await ctx.send(text)

    ########### Inital Party attempts using dict storage but it is easier to just do some string checking --> no need to store
    # @commands.command(hidden=True)
    # async def party(self, ctx):
    #     """Party Time!"""
    #     party_emojis = ('🎉','🎈','🎂','🍾','🍻','🥂','🍸','🎊','💃','🎇','🎆','🕺','🎶','🙌','🍰','🍹','👯','🎁')
    #     guild_id = str(ctx.guild.id)
    #     if guild_id not in self.tmp_channel_storage:
    #         self.tmp_channel_storage[guild_id] = {}
    #         for channel in ctx.guild.channels:
    #             new_name = f'{choice(party_emojis)} {channel.name} {choice(party_emojis)}'
    #             if len(new_name) <= 32:
    #                 await channel.edit(name=new_name)
    #                 self.tmp_channel_storage[guild_id][str(channel.id)] = channel.name
    #             await sleep(2)
    #         await ctx.send('Let the Party Begin!')
    #     else:
    #         await ctx.send('Guild already in storage')

    # @commands.command(hidden=True)
    # async def unparty(self, ctx):
    #     guild_id = str(ctx.guild.id)
    #     if guild_id in self.tmp_channel_storage:
    #         for channel_id in self.tmp_channel_storage[guild_id]:
    #             channel = self.bot.get_channel(int(channel_id))
    #             await channel.edit(name=self.tmp_channel_storage[guild_id][channel_id])
    #             await sleep(2)
    #         await ctx.send('Party\'s Over!')
    #         del self.tmp_channel_storage[guild_id]
    #     else:
    #         await ctx.send('Guild not in storage')
    
    # @commands.command(hidden=True)
    # async def show(self, ctx):
    #     if self.tmp_channel_storage:
    #         await ctx.send(self.tmp_channel_storage)
    #     else:
    #         await ctx.send('Nothing to show')
    ###########

    @commands.command(hidden=True)
    async def party(self, ctx):
        """
        Party Time!
        
        Puts party emojis in every channel name!
        """
        party_emojis = ('🎉','🎈','🎂','🍾','🍻','🥂','🍸','🎊','💃','🎇','🎆','🕺','🎶','🙌','🍰','🍹','👯','🎁')
        for channel in ctx.guild.channels:
            new_name = '{0} {1} {0}'.format(choice(party_emojis), channel.name)
            if len(new_name) <= 100:
                await channel.edit(name=new_name)
                await sleep(2)
        await ctx.send('Let the Party Begin!')

    @commands.command(hidden=True, aliases=['unparty'])
    async def clean_channels(self, ctx, *, clear_type = None):
        """
        Removes party emojis from all channel names.
        """
        if clear_type == 'rip':
            emojis = ('💀', '🕯️', '🙏', '🪦', '😪', '😩', '😤', '🌹', '🧎‍♂️', '👏', '🇷ℹ️🅿️', '🏺', '🧲')
        else:
            emojis = ('🎉','🎈','🎂','🍾','🍻','🥂','🍸','🎊','💃','🎇','🎆','🕺','🎶','🙌','🍰','🍹','👯','🎁')
        for channel in ctx.guild.channels:
            clean_name = str(channel.name)
            for emoji in emojis:
                clean_name = clean_name.replace(emoji, '')
            clean_name = clean_name.strip()
            if clean_name != channel.name:
                await channel.edit(name=clean_name)
                await sleep(2)
        await ctx.send('Channel names cleaned up!')

    @commands.command(aliases=['dark', 'hide'])
    async def go_dark(self, ctx):
        await self.bot.change_presence(status=discord.Status.invisible)
        await ctx.message.add_reaction('🕵️')
        await sleep(5)
        await ctx.message.delete()
    
    @commands.command(aliases=['show'])
    async def undark(self, ctx):
        await self.bot.change_presence(status=discord.Status.online)

    @commands.command()
    async def react(self, ctx, message: discord.Message, reaction = None):
        await ctx.message.delete()
        if reaction == None:
            await ctx.message.author.send('Provide a reaction `message reaction`')
        await message.add_reaction(reaction)
    
    @commands.command(aliases=['emojibomb'])
    async def poofbomb(self, ctx, emoji=None):
        if emoji == None:
            emoji = '🌫️'
            await ctx.send(""":fog::fog::fog:<:blank:743650775141711983>:fog::fog::fog:<:blank:743650775141711983>:fog::fog::fog:<:blank:743650775141711983>:fog::fog::fog:
:fog:<:blank:743650775141711983>:fog:<:blank:743650775141711983>:fog:<:blank:743650775141711983>:fog:<:blank:743650775141711983>:fog:<:blank:743650775141711983>:fog:<:blank:743650775141711983>:fog:
:fog::fog::fog:<:blank:743650775141711983>:fog:<:blank:743650775141711983>:fog:<:blank:743650775141711983>:fog:<:blank:743650775141711983>:fog:<:blank:743650775141711983>:fog::fog::fog:
:fog:<:blank:743650775141711983><:blank:743650775141711983><:blank:743650775141711983>:fog:<:blank:743650775141711983>:fog:<:blank:743650775141711983>:fog:<:blank:743650775141711983>:fog:<:blank:743650775141711983>:fog:
:fog:<:blank:743650775141711983><:blank:743650775141711983><:blank:743650775141711983>:fog::fog::fog:<:blank:743650775141711983>:fog::fog::fog:<:blank:743650775141711983>:fog:""")
        else:
            await ctx.send(emoji)
        num = randint(20,50)
        async for message in ctx.channel.history(limit=num):
            if randint(1,3) == 2:
                await message.add_reaction(emoji)


    async def _get_first_of_last_msg_group(self, ctx): # Find last msg in channel from user
        last_msg_time = None
        async for message in ctx.channel.history(limit=30, before=ctx.message):
            if message.author == ctx.message.author:
                # Last msg sent has been found
                if last_msg_time == None:
                    last_msg_time = message.created_at

                # continue checking the messages (in that chunk) that are within sec_diff_for_msgs_to_count_as_batch sec of the last msg sent by the user, if not then the last msg ust have been the first of the group
                if (last_msg_time-message.created_at).total_seconds() > self.sec_diff_for_msgs_to_count_as_batch:
                    return message # Return msg that is over as purge deletes msgs after specified

            else: # Stop if we find someone else's msg
                if last_msg_time != None:
                    return message # Return that other users msg as purge deletes msgs after specified
        return #No messages from user were found

    @commands.command()
    async def regret(self, ctx):
        """
        Clears the last batch (up to 10) of messages from user
        Searches the last 30 msgs in channel for a msg batch from user 
        messages is part of the batch if it was sent within self.sec_diff_for_msgs_to_count_as_batch sec of the last one in the batch, default: 8
        """
        await ctx.message.delete()
        first_msg_of_group = await self._get_first_of_last_msg_group(ctx)
        if first_msg_of_group:
            def is_me(m):
                return m.author == ctx.message.author
            await ctx.channel.purge(limit=10, after=first_msg_of_group, check=is_me)

    @commands.command(aliases=['batch_size', 'batch_time', 'batch_diff', 'regret_size', 'regret_time', 'regret_diff'])
    async def batch(self, ctx, val: int):
        options = await read_data('options')
        self.sec_diff_for_msgs_to_count_as_batch = val
        options['sec_diff_for_msgs_to_count_as_batch'] = val
        await write_data('options', options)
        await ctx.send(f'{ctx.author.mention} set `sec_diff_for_msgs_to_count_as_batch` to **{val}** sec')

def setup(bot):
    bot.add_cog(Tools(bot))

from discord.ext import tasks, commands
from utils import read_data, write_data
from random import choice, randint
from asyncio import sleep, TimeoutError
import discord
from typing import Union
import json
from datetime import timedelta

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
        self.sleep_time = 0.5

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

    # @commands.command()
    # async def test(self, ctx):
    #     flip_type = choice(('yes', 'yes', 'no', 'no', 'maybe'))
    #     colour_map = {
    #         'yes': discord.Colour.green,
    #         'maybe': discord.Colour.yellow,
    #         'no': discord.Colour.red
    #     }
    #     result_embed = discord.Embed(title=flip_type.upper(), description=f'↳:stopwatch: flip expired!', colour=colour_map[flip_type]())
    #     result_embed.set_footer(text=f'by NOM#7666')

    #     await ctx.reply(embed=result_embed, mention_author=False)

    # @commands.command(brief="Send a message with a button!") # Create a command inside a cog
    # async def button(self, ctx):
    #     view = discord.ui.View() # Establish an instance of the discord.ui.View class
    #     style = discord.ButtonStyle.green  # The button will be gray in color
    #     item = discord.ui.Button(style=style, label="Read the docs!", url="https://discordpy.readthedocs.io/en/master")  # Create an item to pass into the view class.
    #     view.add_item(item=item)  # Add that item into the view class
    #     await ctx.send("This message has buttons!", view=view)  # Send your message with a button.

    # @commands.command()
    # async def test(self, ctx):
    #     from datetime import datetime
    #     await ctx.send(timedelta(seconds=(ctx.message.created_at-ctx.message.created_at).total_seconds()))
    #     # work out how to do now - created at (native and aware error :( )

    @commands.command(brief="Send the last few dms between user and the bot") # Create a command inside a cog
    async def dms(self, ctx, user: discord.User, count: int=None, reverse=None):
        async with ctx.typing():
            dm_channel = await user.create_dm()
            to_send = f'**DMs from {user}**'
            to_send += f'\n{"-"*len(to_send)}'
            files = []
            async for message in dm_channel.history(limit=count+1 if reverse else count, oldest_first=True if reverse else False): #count+1 bc at the top of a dm the first msg is weird and empty
                if message.attachments:
                    for attachment in message.attachments:
                        files.append(await attachment.to_file())
                if len(to_send + '\n' + message.content) >= 2000:
                    await ctx.send(to_send, files=files)
                    to_send = ''
                    files = []
                elif len(files) >= 3:
                    await ctx.send(files=files)
                    files = []
                else:
                    to_send += '\n' + message.content
            if to_send:
                await ctx.send(to_send, files=files)
        await ctx.send('`Complete!`')

    @commands.command(hidden=True)
    async def sudo(self, ctx, who: Union[discord.Member, discord.User], *, text=None):
        """Impersonate a user (must share a server with this bot)"""
        await ctx.message.delete()
        files = []
        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                files.append(await attachment.to_file())
        webhook = await ctx.channel.create_webhook(name='DeletedUser')
        await webhook.send(content=text if text != None else '', username=who.display_name, avatar_url=who.display_avatar.url, files=files)
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
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass
        await ctx.send(text)

    async def check_deep_perms(self, perms_list, perms_map, role_or_member, member, channel):
        if isinstance(role_or_member, discord.Member):
            if role_or_member != member:
                return perms_map #Exit out if member is not the one in question
        if isinstance(role_or_member, discord.Role):
            if role_or_member not in member.roles:
                return perms_map #Exit out if member does not have role in question

        overwrite = channel.overwrites[role_or_member]
        if not overwrite.is_empty():
            for perm in overwrite:
                if perm[0] in perms_list:
                    if perm[1]:
                        if perm[0] not in perms_map:
                            perms_map[perm[0]] = []
                        everyone_string = '`@everyone`'
                        perms_map[perm[0]].append(f"{channel.mention}{f'-{role_or_member.mention if not role_or_member.is_default() else everyone_string}' if isinstance(role_or_member, discord.Role) else ''}")
        return perms_map

    @commands.command(aliases=['power'])
    async def perms(self, ctx, member: discord.Member, read_messages=None):
        """Shows an embed of power perms and what roles give power to the user"""
        async with ctx.typing():
            perms_list = ['administrator', 'ban_members', 'create_instant_invite', 'deafen_members', 'kick_members', 'manage_channels', 'manage_emojis', 'manage_emojis_and_stickers', 'manage_events', 'manage_guild', 'manage_messages', 'manage_nicknames', 'manage_roles', 'manage_threads', 'manage_webhooks', 'mention_everyone', 'move_members', 'mute_members', 'view_audit_log']
            if read_messages: #Whether or not to show the read_mesasges perm
                perms_list.insert(0, 'read_messages')
            perms_map = {}
            for role in member.roles:
                for perm in role.permissions: #perm --> eg. ('send_messages_in_threads', True)
                    if perm[0] in perms_list:
                        if perm[1]:
                            if perm[0] not in perms_map:
                                perms_map[perm[0]] = []
                            perms_map[perm[0]].append(role.mention if not role.is_default() else '`@everyone`')

            for channel in ctx.guild.channels:
                for role_or_member in channel.overwrites:
                    perms_map = await self.check_deep_perms(perms_list, perms_map, role_or_member, member, channel)

            e = discord.Embed(colour = 0x2F3136)
            e.set_author(name=f'{member}\'s Perms', icon_url=member.display_avatar.url)
            value = None
            count = 0
            for perm in perms_map:
                for string in perms_map[perm]:
                    if len(f'{value}, {string}') < 1024:
                        if value:
                            value = f'{value}, {string}'
                        else:
                            value = string
                    else:
                        if len(e) + len(perm) + len(value) > 6000:
                            await ctx.reply(embed=e, allowed_mentions=discord.AllowedMentions.none())
                            count += 1
                            e = discord.Embed(colour = 0x2F3136)
                            e.set_author(name=f'{member}\'s Perms {count}', icon_url=member.display_avatar.url)
                        e.add_field(name=perm, value=value)
                        value = string
                if value:
                    if len(e) + len(perm) + len(value) > 6000:
                        await ctx.reply(embed=e, allowed_mentions=discord.AllowedMentions.none())
                        count += 1
                        e = discord.Embed(colour = 0x2F3136)
                        e.set_author(name=f'{member}\'s Perms {count}', icon_url=member.display_avatar.url)
                    e.add_field(name=perm, value=value)
                    value = None
        if count:
            func = ctx.send
        else:
            func = ctx.reply
        await func(embed=e, allowed_mentions=discord.AllowedMentions.none())

    async def role_perms_embed(self, role):
        role_perms = []
        embed = discord.Embed(description=role.mention, colour=role.colour)
        for perm in role.permissions:
            if perm[1]:
                role_perms.append(perm[0])
        if not role_perms:
            role_perms = ['Role has no perms but does not match `discord.Permissions.none()` :thinking:']
        embed.add_field(name='Perms', value='\n'.join(role_perms))
        return embed

    @commands.command(aliases=['rolesperms','role_perms', 'roleperms'])
    @commands.guild_only()
    async def roles(self, ctx):
        """Shows an embed summarising perms every role with perms"""
        no_perms_count = 0
        embeds = []
        for role in ctx.guild.roles:
            if role.permissions == discord.Permissions.none():
                no_perms_count += 1
            else:
                embed = await self.role_perms_embed(role)
                if len(embeds) < 10:
                    embeds.append(embed)
                else:
                    embeds.append(embed)
                    await ctx.send(embeds=embeds, allowed_mentions=discord.AllowedMentions.none())
                    embeds = []
        if embeds:
            await ctx.send(embeds=embeds, allowed_mentions=discord.AllowedMentions.none())
        await ctx.send(f'Done - There were {no_perms_count} roles with no perms')

    @commands.command()
    @commands.guild_only()
    async def manageroles(self, ctx):
        """Iterates through all roles waiting for the user to select whether to clear it of perms or not"""
        no_perms_count = 0
        for role in ctx.guild.roles:
            if role.permissions == discord.Permissions.none():
                no_perms_count += 1
            else:
                msg = await ctx.send(embed=await self.role_perms_embed(role), allowed_mentions=discord.AllowedMentions.none())
                await msg.add_reaction('🧼')
                await msg.add_reaction('❌')

                def check(reaction, user):
                    return user == ctx.message.author and \
                        str(reaction.emoji) in ('🧼','❌')

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=30.0)
                except TimeoutError:
                    await ctx.send('Took too long, `aborting`')
                    return
                else:
                    if reaction.emoji == '❌':
                        await msg.clear_reactions()
                    elif reaction.emoji == '🧼':
                        try:
                            await role.edit(permissions=discord.Permissions.none(), reason='🧹🧹🧹')
                            await msg.delete()
                            no_perms_count += 1
                        except discord.errors.Forbidden:
                            await msg.clear_reactions()

        await ctx.send(f'Done - There were {no_perms_count} roles with no perms')

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

    @commands.group(aliases=['massrole'])
    @commands.guild_only()
    async def mass_role(self, ctx):
        pass

    @mass_role.command(aliases=['add'])
    async def give(self, ctx, role: discord.Role, *, reason=None):
        msg = await ctx.reply(f'Queued `add role` to **~{ctx.guild.member_count} members**\n  --> Eta: **{str(timedelta(seconds=int(ctx.guild.member_count*self.sleep_time)))}**')
        count = 0
        for member in ctx.guild.members:
            if role not in member.roles:
                await member.add_roles(role, reason=reason)
                count += 1
                await sleep(self.sleep_time)
        await msg.edit(f':white_check_mark: `Added` {role.mention} to **{count} members** :grimacing:', allowed_mentions=discord.AllowedMentions.none())

    @mass_role.command(aliases=['take'])
    async def remove(self, ctx, role: discord.Role, *, reason=None):
        msg = await ctx.reply(f'Queued `remove role` to **~{ctx.guild.member_count} members**\n  --> Eta: **{str(timedelta(seconds=int(ctx.guild.member_count*self.sleep_time)))}**')
        count = 0
        for member in ctx.guild.members:
            if role in member.roles:
                await member.remove_roles(role, reason=reason)
                count += 1
                await sleep(self.sleep_time)
        await msg.edit(f':white_check_mark: `Removed` {role.mention} from **{count} members** :grimacing:', allowed_mentions=discord.AllowedMentions.none())

def setup(bot):
    bot.add_cog(Tools(bot))

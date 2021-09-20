from discord.ext import commands
import discord
import re

rog_server_id = 593542699081269248

no_mentions = discord.AllowedMentions.none()

class Auto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.callouts = {}

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.guild and message.guild.id == rog_server_id and not message.author.bot:
    #         content = message.content.lower()
    #         # spaces_count = content.count(' ')
    #         # matched_int_ranges = re.search(r"(?:^|[^\d])(\d{1,3}-\d{1,3})(?:[^\d]|$)|(?:[^\d-](\d{1,3}(?:,[\d]{1,3})+))") #Maths teacher shenanegans
            
    async def _on_delete_handler(self, message):
        if message.id in self.callouts:
            sent = await message.channel.send(self.callouts[message.id], allowed_mentions=no_mentions)
            self.callouts[sent.id] = str(self.callouts[message.id])
            del self.callouts[message.id]
        elif message.guild and message.guild.id == rog_server_id and not message.author.bot:
            content = message.content.lower()
            possible_role_mentions = re.findall(r"<@&\d{18}>", content)
            if possible_role_mentions:
                string_to_send = f"{message.author.mention} mentioned: {', '.join(possible_role_mentions)}"
                sent = await message.channel.send(string_to_send, allowed_mentions=no_mentions)
                self.callouts[sent.id] = string_to_send

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        await self._on_delete_handler(message)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        for message in messages:
            await self._on_delete_handler(message)

def setup(bot):
    bot.add_cog(Auto(bot))




















# if content in ('hold up', 'hol up'):
            #     officer_emojis = (':police_officer:', ':man_police_officer:', ':woman_police_officer:')
            #     await message.channel.send(f':raised_hand:{choice(officer_emojis)}:raised_back_of_hand:')
            # if content.find('another day') != -1 and spaces_count <= 3:
            #     #Add some kind of cooldown so ppl cant spam it so it seems more sentient
            #     another_say_emojis = ('<:arv1:849391638254190622><:arv2:849391640506662912>', ':pensive:', ':ok_hand:', ':weary:', '<:pooooG:774059516328804352>', '<:troll:777839853487783956>', '<:okcool:804285714312986645>')
            #     await message.channel.send(f'another say {choice(another_say_emojis)}')
            # if content.find('another say') != -1 and spaces_count <= 3:
            #     await message.add_reaction('<:okcool:804285714312986645>')
            # if message.author.id != 421362214558105611 and content.find('true say') != -1 and spaces_count <= 6:
            #     no_emojis = ('😤', '😮‍💨', '😡', '🤬', '🤫', '🤔', '🙄', '😵', '🤮', '🥸', '🤡', '👺', '🙅', '🙅‍♀️', '🙅‍♂️', '⚔️', '❤️‍🔥', '❌', '💢', '❗', '‼️', '⁉️', '⚠️', '✖️', '🃏')
            #     await message.add_reaction(choice(no_emojis))
            # if content.find('bless up') != -1 and spaces_count <= 3:
            #     bless_emojis = ('🙏', '😬')
            #     await message.add_reaction(choice(bless_emojis))
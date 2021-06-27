from discord.ext import commands
from random import choice

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            content = message.content.lower()
            spaces_count = content.count(' ')
            if content == 'hold up':
                await message.channel.send(':raised_hand::woman_police_officer::raised_back_of_hand:')
            elif content.find('another day') != -1 and spaces_count <= 3:
                #Add some kind of cooldown so ppl cant spam it so it seems more sentient
                another_say_emojis = ('<:arv1:849391638254190622><:arv2:849391640506662912>', ':pensive:', ':ok_hand:', ':weary:', '<:pooooG:774059516328804352>', '<:troll:777839853487783956>', '<:okcool:804285714312986645>')
                await message.channel.send(f'another say {choice(another_say_emojis)}')
            elif content.find('another say') != -1 and spaces_count <= 3:
                await message.add_reaction('<:okcool:804285714312986645>')
            elif message.author.id != 421362214558105611 and content.find('true say') != -1 and spaces_count <= 6:
                no_emojis = ('😤', '😮‍💨', '😡', '🤬', '🤫', '🤔', '🙄', '😵', '🤮', '🥸', '🤡', '👺', '🙅', '🙅‍♀️', '🙅‍♂️', '⚔️', '❤️‍🔥', '❌', '💢', '❗', '‼️', '⁉️', '⚠️', '✖️', '🃏')
                await message.add_reaction(choice(no_emojis))

def setup(bot):
    bot.add_cog(Events(bot))
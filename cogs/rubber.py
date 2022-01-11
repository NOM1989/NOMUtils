from discord.ext import commands
import discord
from difflib import get_close_matches

from random import choice
# from asyncio import sleep

# rubber_table_sql = """CREATE TABLE IF NOT EXISTS rubber (
#   id SERIAL PRIMARY KEY,
#   link TEXT NOT NULL UNIQUE,
#   type VARCHAR NOT NULL CONSTRAINT valid_type CHECK (type in ('yes', 'no', 'maybe')),
#   rarity SMALLINT NOT NULL CONSTRAINT valid_rarity CHECK (rarity BETWEEN 0 AND 3),
#   credit BIGINT,
#   created TIMESTAMP DEFAULT now(),
#   uses INT DEFAULT 0
# );"""

# user_table_sql = """CREATE TABLE IF NOT EXISTS users (
# 	id BIGINT PRIMARY KEY,
#   	highest_rubber_rarity SMALLINT,
# );"""

#Rarity
# 0 - common
# 1 - uncommon
# 2 - rare
# 3 - legendary

#Set rariy column to int

# Define a simple View that waits till the OK button pressed or timeout
class Ok_Button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label='OK', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label='Credit', style=discord.ButtonStyle.grey, disabled=True)
    async def credit(self, button: discord.ui.Button, interaction: discord.Interaction):
        pass

class Rubber(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    # @commands.command()
    # async def rtest(self, ctx):
    #     con = self.bot.pool
    #     query = """SELECT * FROM rubber;"""
    #     print(await con.fetch(query))

    @commands.group()
    async def rubber(self, ctx):
        pass

    # @rubber.command()
    # async def view(self, ctx):
    #     con = self.bot.pool
    #     query = """SELECT * FROM rubber;"""
    #     print(await con.fetch(query))
    
    # @rubber.command()
    # async def viewall(self, ctx):
    #     con = self.bot.pool
    #     query = """SELECT id, link, type, rarity FROM rubber;"""
    #     all_flips = await con.fetch(query)
    #     for flip in all_flips:
    #         await ctx.send(f'{flip["type"]} - rarity: {flip["rarity"]},id: {flip["id"]}\n{flip["link"]}')
    #         await sleep(2)

    async def _generate_flip_result_embed(self, ctx, flip_type, credit):
        colour_map = {
            'yes': discord.Colour.green,
            'maybe': discord.Colour.yellow,
            'no': discord.Colour.red
        }
        result_embed = discord.Embed(title=flip_type.upper(), colour=colour_map[flip_type]())
        # result_embed.set_footer(text=f'⏱ video hidden!')

        return result_embed
    
    @rubber.command()
    async def flip(self, ctx):
        con = self.bot.pool
        #Potentially add some kind of rarity % chance system so its not just based on how many of each rarity exist

        flip_type = choice(('yes', 'yes', 'no', 'no', 'maybe')) #Makes maybe more rare

        #COALESCE - returns the first non-null argument.
        query = """SELECT COALESCE((
                    SELECT MAX (rarity)
                    FROM rubber
                    WHERE credit = $1
                    ), 0)"""
        max_rarity = await con.fetchval(query, ctx.author.id)

        pred = 'type = $1 AND rarity <= $2'
        query = f"""SELECT id, link, credit
                    FROM rubber
                    WHERE {pred}
                    OFFSET FLOOR(RANDOM() * (
                        SELECT COUNT(*)
                        FROM rubber
                        WHERE {pred}
                    ))
                    LIMIT 1;"""

        flip = await con.fetchrow(query, flip_type, max_rarity)

        view = Ok_Button()
        potential_credit = self.bot.get_user(flip["credit"])
        if potential_credit:
            view.credit.label = f'Credit: {potential_credit}'
        
        # uses_query = """SELECT uses
        #             FROM rubber
        #             WHERE id = $1;"""
        # await ctx.send(f'Uses: {await con.fetchval(uses_query, flip["id"])}') #Testing

        #Increase uses by 1
        query = """UPDATE rubber
                    SET
                        uses = uses + 1
                    WHERE
                        id = $1;"""
        await con.execute(query, flip["id"])
        
        # await ctx.send(f'Uses: {await con.fetchval(uses_query, flip["id"])}') #Testing

        flip_message = await ctx.reply(flip["link"], view=view, allowed_mentions=discord.AllowedMentions.none())
        # Wait for the View to stop listening for input...
        await view.wait()
        await flip_message.edit(content='Landed on ⤦', embed=await self._generate_flip_result_embed(ctx, flip_type, flip["credit"]), view=None, allowed_mentions=discord.AllowedMentions.none())


    async def _check_vaild_data(self, thing, possible_things):
        possible_thing = get_close_matches(thing, possible_things, n=1)
        if not possible_thing: #Is a list of 1
            return False
        else:
            return possible_thing[0]

    # @rubber.command()
    # async def add(self, ctx, link=None, flip_type=None, rarity='common', credit=None):
    #     rarities = ('common', 'uncommon', 'rare', 'legendary')
    #     flip_types = ('yes', 'no', 'maybe')

    #     if link == None or flip_type == None:
    #         await ctx.send(f'A **{"link" if link == None else "flip_type"}** must be provided - `link flip_type rarity credit`')

    #     else:
    #         if flip_type not in flip_types:
    #             flip_type = await self._check_vaild_data(flip_type, flip_types)
    #             if not flip_type:
    #                 await ctx.send('That is not a valid flip_type!')
    #                 return

    #         # if rarity not in rarities:
    #         #     rarity = await self._check_vaild_data(rarity, rarities)
    #         #     if not rarity:
    #         #         await ctx.send('That is not a valid rarity!')
    #         #         return

    #         if not link.startswith('https://'):
    #             if link.startswith('!v$'):
    #                 link = link[3:]
    #             else:
    #                 await ctx.send('That looks like an invalid link :thinking: - If you\'re sure it\'s valid prepend **!v$** (eg. `!v$https://`)')
    #                 return
            
    #         con = self.bot.pool
    #         query = """INSERT INTO rubber (link, type, rarity, credit)
    #                     VALUES ($1, $2, $3, $4)
    #                     ON CONFLICT link DO NOTHING;"""
    #         await con.execute(query, link, flip_type, int(rarity), int(credit))

def setup(bot):
    bot.add_cog(Rubber(bot))





#SQL DUMP
# query = """SELECT exists (SELECT 1 
#                 FROM table
#                 WHERE column = <value>
#                 LIMIT 1);"""

# query = """SELECT *
#         FROM rubber
#         WHERE type = $1 AND rarity = $2
#         ORDER BY random()
#         LIMIT 1;"""

"""With cte_rarity AS (
                      SELECT COALESCE((
                        SELECT MAX (rarity)
                        FROM rubber
                        WHERE credit = $2
                      ), 0)
                    )
                SELECT id, link FROM rubber
                    WHERE type = $1 AND rarity <= cte_rarity
                    OFFSET FLOOR(RANDOM() * (
                      SELECT COUNT(*)
                      FROM rubber
                      WHERE type = $1 AND rarity <= cte_rarity
                    ))
                    LIMIT 1;"""

#Initial DB insert
# INSERT INTO rubber (link, type, rarity, credit)
# 	VALUES
#     ('https://cdn.discordapp.com/attachments/531549574645678082/860213507508666398/video0.mov', 'maybe', 3, 163595812960468992),
#     ('https://cdn.discordapp.com/attachments/531549574645678082/860972722071011328/video0.mov', 'yes', 3, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/852279897330286642/888818915776548884/fire.mp4', 'no', 3, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/531549574645678082/860984469832990770/video0.mov', 'no', 1, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/852279897330286642/888820844002938950/IMG_6551.mov', 'maybe', 1, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/852279897330286642/888831031438880848/IMG_6558.mov', 'yes', 1, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/852279897330286642/888831102691737620/IMG_6559.mov', 'maybe', 1, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/852279897330286642/865177017048891402/IMG_6563.mov', 'yes', 0, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/852279897330286642/865177021755818004/IMG_6569.mov', 'yes', 0, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/852279897330286642/865177213821255700/IMG_6563.mov', 'maybe', 0, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/852279897330286642/865177358415560724/IMG_6563.mov', 'maybe', 0, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/852279897330286642/865178117394923520/IMG_6569.mov', 'maybe', 0, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/852279897330286642/865178910807687208/IMG_6569.mov', 'no', 0, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/852279897330286642/865182756051877908/IMG_6569.mov', 'no', 0, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/852279897330286642/865182821978996746/IMG_6569.mov', 'no', 0, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/852279897330286642/888823663934177380/IMG_6560.mov', 'no', 0, 421362214558105611),
#     ('https://cdn.discordapp.com/attachments/852279897330286642/888824248158806026/IMG_6563.mov', 'no', 0, 421362214558105611);
from PIL import Image, ImageDraw, ImageFont
from .utils.context import Context
from discord.ext import commands
from typing import Union
from bot import NOMUtils
from io import BytesIO
import discord

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot: NOMUtils = bot

    async def cog_check(self, ctx: Context):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def wanted(self, ctx: Context, who: Union[discord.Member, discord.User] = None, *text: str):
        AVATAR_SIZE = 396
        AVATAR_BORDER = 4
        text = ' '.join(text)[:18].upper()

        if who == None:
            who = ctx.message.author

        async with ctx.typing():
            wanted = Image.open('resources/wanted.jpg').convert('RGBA')
            AVATAR_TOP_LEFT = ((wanted.width-AVATAR_SIZE)//2,185) # (x,y)

            with BytesIO() as buffer:
                await who.display_avatar.save(buffer)

                avatar = Image.open(buffer).convert('RGBA') # Avatar image
                avatar.alpha_composite(Image.new('RGBA',avatar.size,(238, 214, 132, 123))) # Add transparent colour overaly

                # Resize avatar image
                avatar = avatar.resize((AVATAR_SIZE,AVATAR_SIZE), resample=Image.Resampling.BICUBIC)
                # Adjust transparency
                avatar.putalpha(170)

                # Combine images
                wanted.alpha_composite(avatar, AVATAR_TOP_LEFT)

                # make a blank image for the text and drawing, initialized to transparent text color
                drawn_image = Image.new("RGBA", wanted.size, (255, 255, 255, 0))
                # get a font
                font = ImageFont.truetype("resources/Nashville-z8w0.ttf", 62)
                # get a drawing context
                draw = ImageDraw.Draw(drawn_image)
                # draw text centraly
                w, h = draw.textsize(text, font=font)
                draw.text(((wanted.width-w)/2,616), text, font=font, fill=(5, 1, 4, 240))

                # draw border
                x = AVATAR_TOP_LEFT[0]
                y = AVATAR_TOP_LEFT[1]
                draw.rounded_rectangle(((x-AVATAR_BORDER, y-AVATAR_BORDER), (x+AVATAR_SIZE+AVATAR_BORDER-1, y+AVATAR_SIZE+AVATAR_BORDER-1)), outline=(40, 20, 0, 120), width=AVATAR_BORDER, radius=AVATAR_BORDER)

                buffer = BytesIO()
                wanted_poster = Image.alpha_composite(wanted, drawn_image)
                wanted_poster.save(buffer, 'PNG')
                buffer.seek(0)
                wanted_poster_image_file = discord.File(buffer, filename=f'wanted.png')
                await ctx.send(file=wanted_poster_image_file)
                buffer.close()

def setup(bot):
    bot.add_cog(Images(bot))
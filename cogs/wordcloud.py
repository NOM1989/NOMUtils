from .utils.context import Context
from discord.ext import commands
from collections import Counter
from numpy import asarray
from bot import NOMUtils
from io import BytesIO
from PIL import Image
import wordcloud
import discord

class WordCloud(commands.Cog):
    def __init__(self, bot):
        self.bot: NOMUtils = bot
        self.cloud_mask = self.create_array()
        
    def create_array(self):
        # load the image and convert into numpy array
        img = Image.open('ERS_mask.png')
        # asarray() class is used to convert PIL images into NumPy arrays
        return asarray(img)

    async def cog_check(self, ctx: Context):
        return await self.bot.is_owner(ctx.author)

    @commands.command(aliases=['wc'])
    async def wordcloud(self, ctx: Context, limit: int = 500, use_mask: bool = True):
        if limit == 0:
            limit = None

        async with ctx.typing():
            if use_mask:
                current_cloud = wordcloud.WordCloud(mask=self.cloud_mask)
            else:
                current_cloud = wordcloud.WordCloud(width=1024, height=768)

            words = Counter()
            
            async for message in ctx.channel.history(limit=limit):
                words.update(current_cloud.process_text(message.clean_content))

            current_cloud.fit_words(dict(words))
            image = current_cloud.to_image()

            with BytesIO() as image_binary:
                image.save(image_binary, 'PNG')
                image_binary.seek(0)
                return await ctx.reply(file=discord.File(image_binary, 'wordcloud.png'), allowed_mentions=discord.AllowedMentions.none())
            
def setup(bot):
    bot.add_cog(WordCloud(bot))


############
# Version with tasks and loops but doesnt work
# and the curretn version is not blocking so...
############

# from .utils.context import Context
# from discord.ext import commands
# from collections import Counter
# import concurrent.futures
# from bot import NOMUtils
# import wordcloud
# import asyncio
# import discord

# class WordCloud(commands.Cog):
#     def __init__(self, bot):
#         self.bot: NOMUtils = bot

#     async def cog_check(self, ctx: Context):
#         return await self.bot.is_owner(ctx.author)

#     async def _make_cloud(self, ctx: Context, limit):
#         current_cloud = wordcloud.WordCloud()
#         words = Counter()
        
#         async for message in ctx.channel.history(limit=limit):
#             words.update(current_cloud.process_text(message.clean_content))

#         current_cloud.fit_words(dict(words))
#         current_cloud.to_file('/Users/nicholasmichau/Downloads/cloud_test.png')
#         image_file = discord.File(current_cloud.to_image().tobytes(), 'wordcloud.png')
#         return await ctx.reply(file=image_file, allowed_mentions=discord.AllowedMentions.none())

#     @commands.command()
#     async def wordcloud(self, ctx: Context, limit: int | str = 500):
#         if isinstance(limit, str) and limit.lower() == 'none':
#             limit = None

#         async with ctx.typing():
#             loop = asyncio.get_running_loop()

#             # CPU-bound operations will block the event loop:
#             # in general it is preferable to run them in a process pool.
#             with concurrent.futures.ProcessPoolExecutor() as pool:
#                 await loop.run_in_executor(pool, lambda: self._make_cloud(ctx, limit))
            
# def setup(bot):
#     bot.add_cog(WordCloud(bot))
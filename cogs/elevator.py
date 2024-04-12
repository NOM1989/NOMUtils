from discord.ext import commands
from bot import NOMUtils
from .utils.context import Context
import discord
import logging
from asyncio import sleep


class Elevator(commands.Cog):
    def __init__(self, bot):
        self.bot: NOMUtils = bot
        self.elevator_guild_id = 1076585149304672459
        self.level_ttf = "𝙻𝚎𝚟𝚎𝚕-"
        self.ttf_map: dict[int, str] = {
            "0": "𝟶",
            "1": "𝟷",
            "2": "𝟸",
            "3": "𝟹",
            "4": "𝟺",
            "5": "𝟻",
            "6": "𝟼",
            "7": "𝟽",
            "8": "𝟾",
            "9": "𝟿",
        }

    async def cog_check(self, ctx):
        return ctx.guild.id == self.elevator_guild_id

    async def cog_load(self):
        """Initialises the floor category on load"""
        self.floor_category = await self.bot.fetch_channel(1076627545711190016)

    def convert_ttf(self, floor):
        """Converts the requested digits to our font"""
        out = ""
        for digit in floor:
            out += self.ttf_map[digit]
        return out

    async def get_floor(self, ctx: Context, floor):
        """Ensures the requested floor exists and returns the channel obj"""
        level_name = self.level_ttf + self.convert_ttf(floor)
        named_channels = [channel.name for channel in ctx.guild.channels]
        if level_name in named_channels:
            channel = ctx.guild.channels[named_channels.index(level_name)]
        else:
            channel = await self.floor_category.create_text_channel(level_name)
        return channel

    def get_channel_by_name(self, ctx: Context, channel_name):
        """Returns the channel obj from the channel name"""
        for channel in ctx.guild.channels:
            if channel.name == channel_name:
                return channel

    @commands.command()
    async def floor(self, ctx: Context, floor: int):
        """
        Allows the user to enter a desired floor to travel to.
        Steps:
         - Check if channel exists
         - Create if not
         - remove perms from old
         - add to new
        """
        with open("floor.txt", "r") as f:
            prev_floor = f.readline()
            print(prev_floor)
            from_channel = await self.get_floor(ctx, prev_floor)
            await from_channel.set_permissions(ctx.message.author, overwrite=None)

        target_channel = await self.get_floor(ctx, str(floor))
        await target_channel.set_permissions(ctx.message.author, read_messages=True)

        with open("floor.txt", "w") as f:
            f.write(str(floor))

        await sleep(3)
        await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(Elevator(bot))

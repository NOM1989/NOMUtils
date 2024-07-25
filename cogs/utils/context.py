# from __future__ import annotations
# from typing import TYPE_CHECKING
#
# if TYPE_CHECKING:
#     from cogs.space import SpaceGame

from discord.ext import commands
from inspect import Parameter
import discord


class Context(commands.Context):
    # # For Space Game
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.spacegame: SpaceGame
    # ###

    def _get_cmd_usage(self):
        """Creates a string describing the usage of the command"""
        usage = f"{self.prefix}{self.invoked_with}"
        for param in self.command.params.values():
            if param.name not in ("self", "ctx"):
                if param.default == Parameter.empty:
                    usage += f" <{param.name}>"
                else:
                    usage += f" [{param.name}]"
        return usage

    async def send_error(self, error_message: str, show_usage: bool = False):
        """Sends an error to the user with optional extra info"""
        to_send = f"{self.bot.my_emojis.error} "
        to_send += error_message
        to_send += f" - `{self._get_cmd_usage()}`" if show_usage else ""
        await self.reply(to_send, allowed_mentions=discord.AllowedMentions.none())

from typing import Any, Dict, List, Optional, TypeVar, Union
from discord.ext import commands
from inspect import Parameter
import discord
from discord.ext.commands.bot import AutoShardedBot, Bot
from discord.ext.commands.core import Command
from discord.ext.commands.view import StringView
from discord.interactions import Interaction
from discord.message import Message

# Types from discord.py/discord/ext/commands/_types.py
_Bot = Union["Bot", "AutoShardedBot"]
BotT = TypeVar("BotT", bound=_Bot, covariant=True)


class Context(commands.Context):
    def __init__(
        self,
        *,
        message: Message,
        bot: BotT,
        view: StringView,
        args: List[Any] = ...,
        kwargs: Dict[str, Any] = ...,
        prefix: Optional[str] = None,
        command: Optional[Command[Any, ..., Any]] = None,
        invoked_with: Optional[str] = None,
        invoked_parents: List[str] = ...,
        invoked_subcommand: Optional[Command[Any, ..., Any]] = None,
        subcommand_passed: Optional[str] = None,
        command_failed: bool = False,
        current_parameter: Optional[Parameter] = None,
        current_argument: Optional[str] = None,
        interaction: Optional[Interaction[BotT]] = None,
    ):
        super().__init__(
            message=message,
            bot=bot,
            view=view,
            args=args,
            kwargs=kwargs,
            prefix=prefix,
            command=command,
            invoked_with=invoked_with,
            invoked_parents=invoked_parents,
            invoked_subcommand=invoked_subcommand,
            subcommand_passed=subcommand_passed,
            command_failed=command_failed,
            current_parameter=current_parameter,
            current_argument=current_argument,
            interaction=interaction,
        )
        self.space_game = 1

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

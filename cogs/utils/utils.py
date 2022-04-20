from discord.ext import commands
from inspect import Parameter
import discord
import json

async def get_webook(bot_user: commands.Bot.user, channel: discord.TextChannel, name: str = 'ERS'):
    '''Gets the named webhook or default if `name` not passed for the specified `channel`'''
    for webhook in await channel.webhooks():
        if webhook.user == bot_user and webhook.name == name:
            return webhook
    return await channel.create_webhook(name=name) #Else make one

def create_args_str(command_callable:callable):
    '''Creates a string of arguments in a way we can display to the user'''
    out = ''
    for param in command_callable.params.values():
        if param.name not in ('self', 'ctx'):
            if param.default == Parameter.empty:
                out += f' <{param.name}>'
            else:
                out += f' [{param.name}]'
    return out

def get_cmd_usage(ctx:commands.Context):
    """Converts the passed input into an error message"""
    args_str = create_args_str(ctx.command)
    return f"{ctx.prefix}{ctx.invoked_with}{args_str if args_str else ''}"


# async def get_enabled(module):
#     '''Returns the time the module was enabled or False if module dissabled'''
#     query = """"""

async def read_data(file_name):
    with open(f'{file_name}.json') as x:
        return(json.load(x))

async def write_data(file_name, data_to_dump):
    with open(f'{file_name}.json', 'w') as x:
        json.dump(data_to_dump, x, indent=2)
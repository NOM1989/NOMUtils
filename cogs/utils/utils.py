from discord.ext import commands
import discord
import json

async def get_webook(bot: commands.Bot, channel: discord.TextChannel, name: str = 'ERS'):
    '''Gets the named webhook or default if `name` not passed for the specified `channel`'''
    for webhook in await channel.webhooks():
        if webhook.user == bot.user and webhook.name == name:
            return webhook
    return await channel.create_webhook(name=name) #Else make one

# async def get_enabled(module):
#     '''Returns the time the module was enabled or False if module dissabled'''
#     query = """"""

async def read_data(file_name):
    with open(f'{file_name}.json') as x:
        return(json.load(x))

async def write_data(file_name, data_to_dump):
    with open(f'{file_name}.json', 'w') as x:
        json.dump(data_to_dump, x, indent=2)
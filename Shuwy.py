#!/usr/bin/env python3

import logging
import logging.handlers
import sys, traceback
import contextlib
import os
import platform
import dotenv
import discord

from dotenv import load_dotenv
from datetime import datetime
from discord.ext import commands
from utilities.embeds import embed_error, set_style
from utilities.db import create_tables, add_guild, remove_guild

# This program requires the use of Python 3.6 or higher due to the use of f-strings.
# Compatibility with Python 3.5 is possible if f-strings are removed.
if sys.version_info[1] < 6 or sys.version_info[0] < 3:
    print('[ERROR] Python 3.6 or + is required.')
    exit()

# Configuration parameters set-up.
dotenv_path = os.path.join(f'{os.path.dirname(sys.argv[0])}/config', '.env')
load_dotenv(dotenv_path)
token = os.getenv('DISCORD_TOKEN')
version = os.getenv('APP_VERSION')

@contextlib.contextmanager # No need to define __enter__() and __exit__() methods.
def logger():
    '''Creates different loggers to keep track of everything.'''

    logs = {'discord': None, 'wavelink': None, 'bot': None}

    if not os.path.exists('logs/lavalink'): # This one is for the Lavalink server
            os.makedirs('logs/lavalink')

    for log_name in logs.keys():
        log = logging.getLogger(log_name)
        # We only need one handler for all the logs.
        if not os.path.exists(f'logs/{log_name}'):
            os.makedirs(f'logs/{log_name}')
        handler = logging.handlers.RotatingFileHandler(filename=f'logs/{log_name}/{log_name}.log', mode='w', backupCount=5, encoding='utf-8', maxBytes=2**22)
        handler.setFormatter(logging.Formatter('%(asctime)s %(name)s: %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S'))
        if os.path.isfile(f'logs/{log_name}/{log_name}.log'):
            handler.doRollover()
        log.addHandler(handler)

        logs[log_name] = log

    #Logging Levels: [CRITICAL] [ERROR] [WARNING] [INFO] [DEBUG] [NOTSET]
    logs['discord'].setLevel(logging.INFO)
    logs['wavelink'].setLevel(logging.DEBUG)
    logs['bot'].setLevel(logging.DEBUG)

    try:
        yield
    finally:
        [log.handlers[0].close() for log in logs.values()]

def get_prefix(bot, message):
    '''A callable Prefix for the bot.
    
    Keyword arguments:
    bot -- the bot object 
    message -- message in the contect '''

    # Notice how you can use spaces in prefixes. Try to keep them simple though.
    prefixes = ['!', '? ', '.']

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow ! to be used in DMs
        return '!'

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)

intents = discord.Intents.all()

description = '''Shuwy is a bot written by `Shunya#1624`. It implements basic moderation functions, automation and music.'''
bot = commands.Bot(command_prefix = get_prefix, owner_id = 125345019199488000, case_insensitive = True, description = description, intents = intents)

bot.version = version
bot.log =logging.getLogger('bot')

@bot.event
async def on_connect():
    '''Event that takes place when the bot has successfully connected to Discord
       Loads cogs and initializes the database when it does not exist.'''

    print('Shuwy is starting up...')
    print('-------------------------------')
    print('Loading Cogs...')
    for cog in os.listdir('.\\cogs'):
        if cog.endswith('.py'):
            try:
                cog = f'cogs.{cog.replace(".py", "")}'
                bot.load_extension(cog)
            except Exception as e:
                print(f'Could not load extension: {e}')
    print('Finished loading Cogs.')
    print('-------------------------------')
    return await create_tables()

@bot.event
async def on_guild_join(guild):
    '''Event that takes place when the bot joins a server.
       Initializes the necessary server parameters in the database.'''

    add_guild(guild)
    message='To get started with the bot, try using some of its cool features:'
    embed = discord.Embed(title=f'Thanks for using Shuwy,  {guild.owner.name}!', description=message, color=discord.Colour.purple())
    embed.add_field(name='!help', value='`-Displays all the commands and how to use them`', inline=False)
    embed.add_field(name='!play <song name>', value='`-Plays the song and displays a cool responsive music player (pause, stop, skip, favourite)`', inline=False)
    embed.add_field(name='!welcome <text>', value='`-Set the welcome message`', inline=False)
    embed.add_field(name='!role_add <channel> <messageid> <emoji> <role>', value='`-Sets a role to be added to a user when he reacts to a pre-defined message with a pre-defined role.`', inline=False)
    embed.add_field(name="If you'd like some custom features, or want to report an issue please leave a comment here:", value="https://github.com/Shunya-sama/Shuwy/issues", inline=False)
    join_message = set_style(embed)
    return await guild.owner.send(embed = join_message)

@bot.event
async def on_guild_remove(guild):
    '''Event that takes place when the bot leaves a server.
       Removes the previously created server parameters in the database.'''

    remove_guild(guild)

@bot.event
async def on_ready():
    '''Event that takes places when the bot has booted up succesfully.'''

    print(f'Succesfully logged in as {bot.user}')
    print(f'• ID: {bot.user.id}')
    print(f'• Shuwy version: {bot.version}')
    print(f'• Discord.py version: {discord.__version__}')
    print(f'• Python version: {platform.python_version()}')
    print('-------------------------------')

    # TO-DO: Change the following line to not include it in the on_ready event. 
    await bot.change_presence(activity=discord.Activity(name=f'!help for info', type=1))
    print(f'Successfully logged in and booted!')

if __name__ == '__main__':
    with logger():
        bot.run(token, bot=True, reconnect=True)
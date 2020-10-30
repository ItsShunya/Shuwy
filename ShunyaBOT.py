#!/usr/bin/env python3

import logging
import logging.handlers
import sys, traceback
import contextlib
import sqlite3
import os
import platform
import dotenv
import discord

from dotenv import load_dotenv
from datetime import datetime
from discord.ext import commands
from utilities.embeds import embed_error, set_style

# This program requires the use of Python 3.6 or higher due to the use of f-strings.
# Compatibility with Python 3.5 is possible if f-strings are removed.
if sys.version_info[1] < 6 or sys.version_info[0] < 3:
    print('[ERROR] Python 3.6 or + is required.')
    exit()

# Configuration parameters set-up.
dotenv_path = os.path.join(f'{os.path.dirname(sys.argv[0])}/config', '.env')
load_dotenv(dotenv_path)
token = os.getenv('DISCORD_TOKEN')
database_path = os.path.join(f'{os.path.dirname(sys.argv[0])}/config', 'database.sqlite')

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

bot.version = '0.0.7'
bot.color = 0xebb145
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
    database = sqlite3.connect(database_path)
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS database(
        guild_id TEXT,
        welcome_msg TEXT,
        welcome_channel_id TEXT,
        welcome_channel_on INTEGER,
        welcome_role_id TEXT,
        welcome_role_on INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reaction(
        emoji TEXT,
        role TEXT,
        message_id TEXT,
        channel_id TEXT,
        guild_id TEXT
        )
    ''')

    database.commit()
    cursor.close()
    database.close()

@bot.event
async def on_guild_join(guild):
    '''Event that takes place when the bot joins a server.
       Initializes the necessary server parameters in the database.'''

    database = sqlite3.connect(database_path)
    cursor = database.cursor()
    sql = ('INSERT INTO database(guild_id, welcome_channel_on, welcome_role_on) VALUES(?, ?, ?)')
    val = (guild.id, 0, 0)
    cursor.execute(sql, val)
    database.commit()
    cursor.close()
    database.close()

@bot.event
async def on_guild_remove(guild):
    '''Event that takes place when the bot leaves a server.
       Removes the previously created server parameters in the database.'''

    database = sqlite3.connect(database_path)
    cursor = database.cursor()
    sql = ('DELETE FROM database WHERE guild_id = ?')
    cursor.execute(sql, (guild.id, ))
    database.commit()
    cursor.close()
    database.close()

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
    await bot.change_presence(activity=discord.Activity(name=f'on {len(bot.guilds)} servers', type=1))
    print(f'Successfully logged in and booted!')

if __name__ == '__main__':
    with logger():
        bot.run(token, bot=True, reconnect=True)
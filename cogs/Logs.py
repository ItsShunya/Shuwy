import discord
from discord.ext import commands

class LogsCog(commands.Cog, name='Logs'):
    '''Cog in charge of logging related functions.'''

    def __init__(self, bot):
        self.bot = bot
        self.hidden = True

def setup(bot):
    bot.add_cog(LogsCog(bot))
    message = 'Logs Cog has been loaded succesfully.'
    print('• ' + f'{message}')
    bot.log.info(f'{message}')
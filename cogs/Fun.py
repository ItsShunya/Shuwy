import discord
from discord.ext import commands
from utilities.embeds import set_style

class FunCog(commands.Cog, name='Fun'):
    '''Cog in charge of the functions made for fun activities.'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        '''Ping-Pong.'''
        embed = discord.Embed(description='Pong!', color=0xebb145)
        await ctx.send(embed=set_style(embed))

    @commands.command(name='coolbot', aliases=['cool', 'dope', 'nice'])
    async def cool_bot(self, ctx):
        '''Is the bot cool?'''
        embed = discord.Embed(color=0xebb145, description='This bot is cool. :)')
        await ctx.send(embed=set_style(embed))

def setup(bot):
    bot.add_cog(FunCog(bot))
    message = 'Fun Cog has been loaded succesfully.'
    print('• ' + f'{message}')
    bot.log.info(f'{message}')
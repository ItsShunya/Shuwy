import discord
from discord.ext import commands
from utilities.embeds import set_style

class MathCog(commands.Cog, name='Math'):
    '''Cog in charge of the mathematical functions.'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='add', aliases=['plus'])
    async def do_addition(self, ctx, first: int, second: int):
        '''A simple command which does addition on two values.'''

        total = first + second
        embed = discord.Embed(title=f'Hello, @**{ctx.author.name}**!', description=f'The sum of **{first}** and **{second}**  is  **{total}**.', color=discord.Colour.purple())  
        await ctx.send(embed=set_style(embed))


def setup(bot):
    bot.add_cog(MathCog(bot))
    message = 'Math Cog has been loaded succesfully.'
    print('• ' + f'{message}')
    bot.log.info(f'{message}')
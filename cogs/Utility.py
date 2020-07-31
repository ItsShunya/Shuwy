import discord
import os
import platform
from discord.ext import commands
from utilities.embeds import embed_error, set_style

class UtilityCog(commands.Cog, name='Utility'):
    '''Cog in charge of different utilities, mostly related with bot (admin) stuff or general events.'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        '''Turns off the bot.'''

        await ctx.send('Shuwy has been shutdown')
        await self.bot.logout()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        '''Loads a Module.'''

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        '''Unloads a Module.'''

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, msg):
        '''Reloads a module.'''

        try:
            if os.path.exists(f'cogs/{msg}.py'):
                self.bot.reload_extension(f'cogs.{msg}')
            else:
                raise ImportError(f'No module named `{msg}.py`')
        except Exception as e:
            message = f'Failed to reload module: `{msg}.py`: {e}'
            await ctx.send(embed=embed_error(message, input1=ctx, input2=e))
        else:
            embed = discord.Embed(description=f'Module `{msg}` has been reloaded succesfully.', color=0xffd500)  
            await ctx.send(embed=set_style(embed))

    @commands.group(invoke_without_command=False)
    @commands.is_owner()
    async def status(self, ctx):
        '''Changes the status of the bot to playing a game, listening to music or streaming.
           Requieres for subcommands to be invoked.'''

        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=0xebb145, title='Available Commands:', description='status streaming <name> <url>\nstatus playing <name>\nstatus watching <name>\nstatus membercount')
            await ctx.send(embed=set_style(embed))

    @status.command()
    async def streaming(self, ctx, name_stream: str, url_stream: str):
        '''Subcomand for "status" that changes the status of the bot to streaming.
        
        Keyword arguments:
        name_stream -- name of the streaming to be displayed
        url_stream -- url of the stream'''

        await self.bot.change_presence(activity=discord.Streaming(name=name_stream, type=1, url=url_stream))
    
    @status.command()
    async def playing(self, ctx, name_game: str):
        '''Subcomand for "status" that changes the status of the bot to playing a game.
        
        Keyword arguments:
        name_game -- name of the game to be displayed'''

        await self.bot.change_presence(activity=discord.Game(name=name_game, type=3))

    @status.command()
    async def watching(self, ctx, name_movie: str):
        '''Subcomand for "status" that changes the status of the bot to watching something.
        
        Keyword arguments:
        name_movie -- name of the movie/series/whatever to be displayed'''

        await self.bot.change_presence(activity=discord.Activity(name=name_movie, type=3))

    @status.command()
    async def membercount(self, ctx):
        '''Subcomand for "status" that changes the status of the bot a count of guilds where it is in.'''

        await self.bot.change_presence(activity=discord.Activity(name=f'on {len(self.bot.guilds)} servers', type=1))

    @commands.command()
    async def info(self, ctx):
        '''Displays general information about the bot'''

        embed = discord.Embed(title=f'{self.bot.user.name} Information', description='\uFEFF', color=0xebb145, timestamp = ctx.message.created_at)

        embed.add_field(name='Bot version:', value=self.bot.version)
        embed.add_field(name='Python Version:', value=platform.python_version())
        embed.add_field(name='Discord.py Version:', value=discord.__version__)
        embed.add_field(name='Total Guilds:', value=len(self.bot.guilds))
        embed.add_field(name='Total Users:', value=len(set(self.bot.get_all_members())))
        embed.add_field(name='Bot Developer:', value='<@125345019199488000>')
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=set_style(embed))

    @commands.command()
    async def help(self, ctx, *cog):
        '''Displays general help about certain commands'''

        if not cog:
            embed = discord.Embed(description='Custom Help', color=0xffd500)
            cog_desc = ''
            for x in self.bot.cogs:
                cog_desc += (f'**{x}** - {self.bot.cogs[x].__doc__}\n')
            embed.add_field(name='Cogs', value=cog_desc[0:len(cog_desc)-1], inline=False)
            await ctx.send(embed=set_style(embed))
        else:
            if len(cog) > 1:
                embed = embed_error('Too many cogs!', input1=ctx)
                await ctx.send('', embed=embed)
            else:
                found = False
                for x in self.bot.cogs:
                    for y in cog:
                        if x == y:
                            embed = discord.Embed(color=0xffd500)
                            scog_info = ''
                            for c in self.bot.get_cog(y).get_commands():
                                if not c.hidden:
                                    scog_info += f'**{c.name}** - {c.help}\n'
                            embed.add_field(name=f'{cog[0]} Module - {self.bot.cogs[cog[0]].__doc__}', value=scog_info)
                            found = True
            if not found:
                for x in self.bot.cogs:
                    for c in self.bot.get_cog(x).get_commands():
                        if c.name == cog[0]:
                            embed = discord.Embed(color=0xffd500)
                            embed.add_field(name=f'{c.name} - {c.help}', value=f'Proper Syntax:\n`{c.qualified_name} {c.signature}`')
                    found = True
                if not found:
                    embed = embed_error('That is not a cog!', input1=ctx)
            await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx, channel:discord.TextChannel):
        '''Creates an invite link for the channel.

        Keyword arguments:
        channel -- channel to invite to'''

        invite = await channel.create_invite()
        await ctx.send(invite)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        '''Event that takes place when a command is called.
           Used for logging purposes.'''

        if ctx.guild is None:
            self.bot.log.info(f'Command was called for execution in a private message     Name: {ctx.prefix}{ctx.command} | Invoker ID: {ctx.author.id}')
        else:
            self.bot.log.info(f'Command was called for execution in a guild      Name: {ctx.prefix}{ctx.command} | Invoker ID: {ctx.author.id}  | Guild ID: {ctx.guild.name} | Guild Name: {ctx.guild.id}')

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        '''Event that takes place when a command is executed correctly.
           Used for logging purposes.'''

        if ctx.guild is None:
            self.bot.log.info(f'Command was executed correctly in a private message     Name: {ctx.prefix}{ctx.command} | Invoker ID: {ctx.author.id}')
        else:
            self.bot.log.info(f'Command was execute correctly in a guild      Name: {ctx.prefix}{ctx.command} | Invoker ID: {ctx.author.id}  | Guild ID: {ctx.guild.name} | Guild Name: {ctx.guild.id}')

def setup(bot):
    bot.add_cog(UtilityCog(bot))
    message = 'Utility Cog has been loaded succesfully.'
    print('• ' + f'{message}')
    bot.log.info(f'{message}')
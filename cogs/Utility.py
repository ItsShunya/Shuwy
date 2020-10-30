import discord
import os
import platform
import asyncio
from discord.ext import commands
from utilities.embeds import embed_error, set_style

class HelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__(command_attrs={ 'help': 'Shows help about the bot, a command, or a category',
	    		                         'cooldown': commands.Cooldown(1, 3.0, commands.BucketType.member)})

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot
        page = -1
        cogs = [name for name, obj in bot.cogs.items() if getattr(bot.get_cog(name), 'hidden', False) != True]
        cogs.sort()

        def check(reaction, user):  # check who is reacting to the message
            return user == ctx.author
        embed = await self.bot_help_paginator(page, cogs)
        help_embed = await ctx.send(embed=embed)  # sends the first help page

        reactions = ('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                     '\N{BLACK LEFT-POINTING TRIANGLE}',
                     '\N{BLACK RIGHT-POINTING TRIANGLE}',
                     '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                     '\N{BLACK SQUARE FOR STOP}',
                     '\N{INFORMATION SOURCE}')  # add reactions to the message
        bot.loop.create_task(self.bot_help_paginator_reactor(help_embed, reactions))
        # this allows the bot to carry on setting up the help command

        while 1:
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60, check=check)  # checks message reactions
            except asyncio.TimeoutError:  # session has timed out
                try:
                    await help_embed.delete()
                except discord.errors.Forbidden:
                    pass
                break
            else:
                try:
                    await help_embed.remove_reaction(str(reaction.emoji), ctx.author)  # remove the reaction 
                except discord.errors.Forbidden:
                    pass

                if str(reaction.emoji) == '⏭':  # go to the last the page
                    page = len(cogs) - 1
                    embed = await self.bot_help_paginator(page, cogs)
                    await help_embed.edit(embed=embed)
                elif str(reaction.emoji) == '⏮':  # go to the first page
                    page = 0
                    embed = await self.bot_help_paginator(page, cogs)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == '◀':  # go to the previous page
                    page -= 1
                    if page is -2:  # check whether to go to the final page
                        page = len(cogs) - 1
                    embed = await self.bot_help_paginator(page, cogs)
                    await help_embed.edit(embed=embed)
                elif str(reaction.emoji) == '▶':  # go to the next page
                    page += 1
                    if page == len(cogs):  # check whether to go to the first page
                        page = 0
                    embed = await self.bot_help_paginator(page, cogs)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == 'ℹ':  # show information help
                    page = -1
                    embed = self.get_information_page()
                    await help_embed.edit(embed=set_style(embed))

                elif str(reaction.emoji) == '⏹':  # delete the message and break from the wait_for
                    await help_embed.delete()
                    break

    async def bot_help_paginator_reactor(self, message, reactions):
        for reaction in reactions:
            await message.add_reaction(reaction)

    async def bot_help_paginator(self, page: int, cogs):
        ctx = self.context
        bot = ctx.bot
        cog = bot.get_cog(cogs[page])  # get the current cog
        all_commands = [command for command in bot.get_cog(cogs[page]).get_commands()]  # filter the commands the user can use

        if (page == -1):
            return set_style(self.get_information_page())

        embed = discord.Embed(title=f'{bot.user.name} | Help with {cog.qualified_name} Cog ({len(all_commands)} commands)    :gear:',
                              description=cog.description, color=discord.Colour.purple())
        embed.set_author(name=f'Page {page + 1}/{len(cogs)}', icon_url=ctx.bot.user.avatar_url)
        for c in cog.walk_commands():
            try:
                result = await c.can_run(ctx)
            except commands.errors.CheckFailure:
                result = False
            if result and not c.hidden:
                signature = self.get_command_signature(c)
                description = self.get_command_description(c)
                if c.parent:  # it is a sub-command
                    embed.add_field(name=f'**╚╡**{signature}', value=description)
                else:
                    embed.add_field(name=signature, value=description, inline=False)
        embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.',
                         icon_url=ctx.bot.user.avatar_url)
        return embed 

    def get_command_signature(self, command):
        """Method to return a commands name and signature"""
        if not command.signature and not command.parent:  # checking if it has no args and isn't a subcommand
            return f'`{self.clean_prefix}{command.name}`'
        if command.signature and not command.parent:  # checking if it has args and isn't a subcommand
            return f'`{self.clean_prefix}{command.name}` `{command.signature}`'
        if not command.signature and command.parent:  # checking if it has no args and is a subcommand
            return f'`{command.name}`'
        else:  # else assume it has args a signature and is a subcommand
            return f'`{command.name}` `{command.signature}`'

    def get_command_aliases(self, command):  # this is a custom written method along with all the others below this
        """Method to return a commands aliases"""
        if not command.aliases:  # check if it has any aliases
            return ''
        else:
            return f'command aliases are [`{"` | `".join([alias for alias in command.aliases])}`]'

    def get_command_description(self, command):
        """Method to return a commands short doc/brief"""
        if not command.short_doc:  # check if it has any brief
            return 'There is no documentation for this command currently'
        else:
            return command.short_doc

    def get_command_longer_description(self, command):
        """Method to return a commands longer doc"""
        if not command.__doc__:  # check if it has any brief
            return 'There is no documentation for this command currently'
        else:
            return command__doc__

    def get_command_help(self, command):
        """Method to return a commands full description/doc string"""
        if not command.help:  # check if it has any brief or doc string
            return 'There is no documentation for this command currently'
        else:
            return command.help

    def get_information_page(self):
        ctx = self.context
        bot = ctx.bot

        embed = discord.Embed(title=f'{bot.user.name} | Help    :gear:', description=bot.description, color=discord.Colour.purple())
        embed.add_field(name=f':information_source:  In this page you will find help for any command',
                        value=f'Use `"{self.clean_prefix}help <command>"` for more info on a command.\n\n'
                              '`<...>` indicates a required argument.\n`[...]` indicates an optional argument.\n\n')
        embed.add_field(name=':asterisk: Button Controls:',
                        value=':track_previous: `First page`\n'
                              ':track_next: `Last page`\n'
                              ':arrow_backward: `Previous page`\n'
                              ':arrow_forward: `Next page`\n'
                              ':stop_button: `Deletes this message`\n'
                              ':information_source: `Shows this message`')
        embed.set_author(name=f'Information page',
                        icon_url=ctx.bot.user.avatar_url)
        return embed

    async def send_cog_help(self, cog):
        ctx = self.context
        bot = ctx.bot
        page = -1
        def check(reaction, user):  # check who is reacting to the message
            return user == ctx.author

        embed = await self.bot_help_cog_paginator(page, cog)
        help_embed = await ctx.send(embed=embed)  # sends the first help page

        reactions = ('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                     '\N{BLACK LEFT-POINTING TRIANGLE}',
                     '\N{BLACK RIGHT-POINTING TRIANGLE}',
                     '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                     '\N{BLACK SQUARE FOR STOP}',
                     '\N{INFORMATION SOURCE}')  # add reactions to the message
        bot.loop.create_task(self.bot_help_paginator_reactor(help_embed, reactions))
        # this allows the bot to carry on setting up the help command

        while 1:
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60, check=check)  # checks message reactions
            except asyncio.TimeoutError:  # session has timed out
                try:
                    await help_embed.delete()
                except discord.errors.Forbidden:
                    pass
                break
            else:
                try:
                    await help_embed.remove_reaction(str(reaction.emoji), ctx.author)  # remove the reaction 
                except discord.errors.Forbidden:
                    pass

                if str(reaction.emoji) == '⏭':  # go to the last the page
                    page = 0
                    embed = await self.bot_help_cog_paginator(page, cog)
                    await help_embed.edit(embed=embed)
                elif str(reaction.emoji) == '⏮':  # go to the first page
                    page = -1
                    embed = await self.bot_help_cog_paginator(page, cog)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == '◀':  # go to the previous page
                    page -= 1
                    if page == -2:  # check whether to go to the final page
                        page = 0
                    embed = await self.bot_help_cog_paginator(page, cog)
                    await help_embed.edit(embed=embed)
                elif str(reaction.emoji) == '▶':  # go to the next page
                    page += 1
                    if page == 1:  # check whether to go to the first page
                        page = -1
                    embed = await self.bot_help_cog_paginator(page, cog)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == 'ℹ':  # show information help
                    embed = self.get_information_page()
                    await help_embed.edit(embed=set_style(embed))

                elif str(reaction.emoji) == '⏹':  # delete the message and break from the wait_for
                    await help_embed.delete()
                    break

    async def bot_help_cog_paginator(self, page: int, cog):
        ctx = self.context
        bot = ctx.bot
        all_commands = [command for command in cog.get_commands()]  # filter the commands the user can use

        if (page == -1):
            return set_style(self.get_information_page())

        embed = discord.Embed(title=f'{bot.user.name} | Help with {cog.qualified_name} Cog ({len(all_commands)} commands)    :gear:',
                              description=cog.description, color=discord.Colour.purple())
        embed.set_author(name=f'Page {page + 1}/{1}', icon_url=ctx.bot.user.avatar_url)
        for c in cog.walk_commands():
            try:
                result = await c.can_run(ctx)
            except commands.errors.CheckFailure:
                result = False
            if result and not c.hidden:
                signature = self.get_command_signature(c)
                description = self.get_command_description(c)
                if c.parent:  # it is a sub-command
                    embed.add_field(name=f'**╚╡**{signature}', value=description)
                else:
                    embed.add_field(name=signature, value=description, inline=False)
        embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.',
                         icon_url=ctx.bot.user.avatar_url)
        return embed

    async def send_group_help(self, group):
        ctx = self.context
        bot = ctx.bot
        page = -1
        def check(reaction, user):  # check who is reacting to the message
            return user == ctx.author

        embed = await self.bot_help_command_paginator(page, group)
        help_embed = await ctx.send(embed=embed)  # sends the first help page

        reactions = ('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                     '\N{BLACK LEFT-POINTING TRIANGLE}',
                     '\N{BLACK RIGHT-POINTING TRIANGLE}',
                     '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                     '\N{BLACK SQUARE FOR STOP}',
                     '\N{INFORMATION SOURCE}')  # add reactions to the message
        bot.loop.create_task(self.bot_help_paginator_reactor(help_embed, reactions))
        # this allows the bot to carry on setting up the help command

        while 1:
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60, check=check)  # checks message reactions
            except asyncio.TimeoutError:  # session has timed out
                try:
                    await help_embed.delete()
                except discord.errors.Forbidden:
                    pass
                break
            else:
                try:
                    await help_embed.remove_reaction(str(reaction.emoji), ctx.author)  # remove the reaction 
                except discord.errors.Forbidden:
                    pass

                if str(reaction.emoji) == '⏭':  # go to the last the page
                    page = 0
                    embed = await self.bot_help_group_paginator(page, group)
                    await help_embed.edit(embed=embed)
                elif str(reaction.emoji) == '⏮':  # go to the first page
                    page = -1
                    embed = await self.bot_help_group_paginator(page, group)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == '◀':  # go to the previous page
                    page -= 1
                    if page == -2:  # check whether to go to the final page
                        page = 0
                    embed = await self.bot_help_group_paginator(page, group)
                    await help_embed.edit(embed=embed)
                elif str(reaction.emoji) == '▶':  # go to the next page
                    page += 1
                    if page == 1:  # check whether to go to the first page
                        page = -1
                    embed = await self.bot_help_group_paginator(page, group)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == 'ℹ':  # show information help
                    embed = self.get_information_page()
                    await help_embed.edit(embed=set_style(embed))

                elif str(reaction.emoji) == '⏹':  # delete the message and break from the wait_for
                    await help_embed.delete()
                    break
        return

    async def bot_help_group_paginator(self, page: int, group):
        ctx = self.context
        bot = ctx.bot

        if (page == -1):
            return set_style(self.get_information_page())

        embed = discord.Embed(title=f'{bot.user.name} | Help with {self.clean_prefix}{group} commands    :gear:',
                              description=' ', color=discord.Colour.purple())
        embed.set_author(name=f'Page {page + 1}/{1}', icon_url=ctx.bot.user.avatar_url)
        try:
            result = await group.can_run(ctx)
        except commands.errors.CheckFailure:
            result = False
        for c in group.commands:
            if result and not c.hidden:
                signature = self.get_command_signature(c)
                description = self.get_command_help(c)
                if c.parent:  # it is a sub-command
                    embed.add_field(name=f'**╚╡**{signature}', value=description)
                else:
                    embed.add_field(name=signature, value=description, inline=False)
        embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.',
                         icon_url=ctx.bot.user.avatar_url)
        return embed

    async def send_command_help(self, command):
        ctx = self.context
        bot = ctx.bot
        page = -1
        def check(reaction, user):  # check who is reacting to the message
            return user == ctx.author

        embed = await self.bot_help_command_paginator(page, command)
        help_embed = await ctx.send(embed=embed)  # sends the first help page

        reactions = ('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                     '\N{BLACK LEFT-POINTING TRIANGLE}',
                     '\N{BLACK RIGHT-POINTING TRIANGLE}',
                     '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                     '\N{BLACK SQUARE FOR STOP}',
                     '\N{INFORMATION SOURCE}')  # add reactions to the message
        bot.loop.create_task(self.bot_help_paginator_reactor(help_embed, reactions))
        # this allows the bot to carry on setting up the help command

        while 1:
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60, check=check)  # checks message reactions
            except asyncio.TimeoutError:  # session has timed out
                try:
                    await help_embed.delete()
                except discord.errors.Forbidden:
                    pass
                break
            else:
                try:
                    await help_embed.remove_reaction(str(reaction.emoji), ctx.author)  # remove the reaction 
                except discord.errors.Forbidden:
                    pass

                if str(reaction.emoji) == '⏭':  # go to the last the page
                    page = 0
                    embed = await self.bot_help_command_paginator(page, command)
                    await help_embed.edit(embed=embed)
                elif str(reaction.emoji) == '⏮':  # go to the first page
                    page = -1
                    embed = await self.bot_help_command_paginator(page, command)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == '◀':  # go to the previous page
                    page -= 1
                    if page == -2:  # check whether to go to the final page
                        page = 0
                    embed = await self.bot_help_command_paginator(page, command)
                    await help_embed.edit(embed=embed)
                elif str(reaction.emoji) == '▶':  # go to the next page
                    page += 1
                    if page == 1:  # check whether to go to the first page
                        page = -1
                    embed = await self.bot_help_command_paginator(page, command)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == 'ℹ':  # show information help
                    embed = self.get_information_page()
                    await help_embed.edit(embed=set_style(embed))

                elif str(reaction.emoji) == '⏹':  # delete the message and break from the wait_for
                    await help_embed.delete()
                    break
    
    async def bot_help_command_paginator(self, page: int, command):
        ctx = self.context
        bot = ctx.bot

        if (page == -1):
            return set_style(self.get_information_page())

        embed = discord.Embed(title=f'{bot.user.name} | Help with {self.clean_prefix}{command}    :gear:',
                              description=' ', color=discord.Colour.purple())
        embed.set_author(name=f'Page {page + 1}/{1}', icon_url=ctx.bot.user.avatar_url)
        try:
            result = await command.can_run(ctx)
        except commands.errors.CheckFailure:
            result = False
        if result and not command.hidden:
            signature = self.get_command_signature(command)
            description = self.get_command_help(command)
            if command.parent:  # it is a sub-command
                embed.add_field(name=f'**╚╡**{signature}', value=description)
            else:
                embed.add_field(name=signature, value=description, inline=False)
        embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.',
                         icon_url=ctx.bot.user.avatar_url)
        return embed

class UtilityCog(commands.Cog, name='Utility', command_attrs=dict(hidden=True)):
    '''Cog in charge of different utilities, mostly related with bot (admin) stuff or general events.'''

    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        '''Turns off the bot.'''

        embed = discord.Embed(color=discord.Colour.purple(), description='Shuwy has been shutdown')
        await ctx.send(embed=set_style(embed))
        await self.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        '''Loads a Module.'''

        try:
            self.bot.load_extension('cogs.' + cog)
        except Exception as e:
            return await ctx.send(embed=embed_error('There was an error while loading the extension.', input1=ctx))
        else:
            embed = discord.Embed(description=f'Module `{cog}` has been loaded succesfully.', color=discord.Colour.purple())  
            return await ctx.send(embed=set_style(embed))

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        '''Unloads a Module.'''

        try:
            self.bot.unload_extension('cogs.' + cog)
        except Exception as e:
            return await ctx.send(embed=embed_error('There was an error while unloading the extension {cog}.', input1=ctx))
        else:
            embed = discord.Embed(description=f'Module `{cog}` has been unloaded succesfully.', color=discord.Colour.purple())  
            return await ctx.send(embed=set_style(embed))

    @commands.command()
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
            return await ctx.send(embed=embed_error(message, input1=ctx, input2=e))
        else:
            embed = discord.Embed(description=f'Module `{msg}` has been reloaded succesfully.', color=discord.Colour.purple())  
            return await ctx.send(embed=set_style(embed))

    @commands.command()
    @commands.is_owner()
    async def reloadall(self, ctx):
        """ Reloads all extensions. """
        error_collection = []
        for file in os.listdir('cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                try:
                    if os.path.exists(f'cogs/{name}.py'):
                        self.bot.reload_extension(f'cogs.{name}')
                    else:
                        raise ImportError(f'No module named `{msg}.py`')
                except Exception as e:
                    message = f'Failed to reload module: `{msg}.py`: {e}'
                    return await ctx.send(embed=embed_error(message, input1=ctx, input2=e))
                else:
                    pass
        embed = discord.Embed(description='Successfully reloaded all extensions', color=discord.Colour.purple())  
        await ctx.send(embed=set_style(embed))

    @commands.group(invoke_without_command=False)
    @commands.is_owner()
    async def status(self, ctx):
        '''Changes the status of the bot to playing a game, listening to music or streaming.
           Requieres for subcommands to be invoked.'''

        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=discord.Colour.purple(), title='Available Commands:', description='status streaming <name> <url>\nstatus playing <name>\nstatus watching <name>\nstatus membercount')
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

    @commands.command(hidden=False)
    async def info(self, ctx):
        '''Displays general information about the bot'''

        embed = discord.Embed(title=f'{self.bot.user.name} Information', description='\uFEFF', color=discord.Colour.purple(), timestamp = ctx.message.created_at)

        embed.add_field(name='Bot version:', value=self.bot.version)
        embed.add_field(name='Python Version:', value=platform.python_version())
        embed.add_field(name='Discord.py Version:', value=discord.__version__)
        embed.add_field(name='Total Guilds:', value=len(self.bot.guilds))
        embed.add_field(name='Total Users:', value=len(set(self.bot.get_all_members())))
        embed.add_field(name='Bot Developer:', value='<@125345019199488000>')
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=set_style(embed))

    @commands.command(hidden=False)
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
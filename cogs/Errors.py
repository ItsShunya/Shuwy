import discord
from discord.ext import commands
from utilities.embeds import embed_error

class ErrorCog(commands.Cog, name='Error'):
    '''Cog in charge of the error handling functions.'''

    def __init__(self, bot):
        self.bot = bot
        self.hidden = True

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        '''Event that takes place when there is an error in a command.
    
        Keyword arguments:
        error -- error message '''

        error = getattr(error, 'original', error)

        if ctx.guild is None:
            self.bot.log.info(f'Command was not executed due to an error     Name: {ctx.prefix}{ctx.command} | Error: {error} | Invoker ID: {ctx.author.id}')
        else:
            self.bot.log.info(f'Command was not executed due to an error     Name: {ctx.prefix}{ctx.command} | Error: {error} | Invoker ID: {ctx.author.id}  | Guild ID: {ctx.guild.name} | Guild Name: {ctx.guild.id}')

        if isinstance(error, commands.CommandNotFound):
            message = 'This is not a valid command'
            return await ctx.send(embed=embed_error(message, input1=ctx))

        elif isinstance(error, commands.CommandOnCooldown):
            if ctx.author.id is self.bot.owner_id:
                ctx.command.reset_cooldown(ctx)
                return await ctx.command.reinvoke(ctx)
            cooldowns = {
                commands.BucketType.default: f'for the whole bot.',
                commands.BucketType.user: f'for you.',
                commands.BucketType.guild: f'for this server.',
                commands.BucketType.channel: f'for this channel.',
                commands.BucketType.member: f'cooldown for you.',
                commands.BucketType.category: f'for this channel category.',
                commands.BucketType.role: f'for your role.'
            }
            return await ctx.send(f'The command `{ctx.command}` is on cooldown {cooldowns[error.cooldown.type]} ')
        
        # Bot lacks permissions.
        elif isinstance(error, commands.BotMissingPermissions):
            permissions = '\n'.join([f'> {permission}' for permission in error.missing_perms])
            message = f'I am missing the following permissions required to run the command `{ctx.command}`.\n{permissions}'
            try:
                return await ctx.send(message)
            except discord.Forbidden:
                try:
                    return await ctx.author.send(message)
                except discord.Forbidden:
                    return

        # User lacks permissions.
        elif isinstance(error, commands.MissingPermissions):
            permissions = '\n'.join([f'> {permission}' for permission in error.missing_perms])
            return await ctx.send(embed=embed_error(f'You are missing the following permissions required to run the command `{ctx.command}`.\n{permissions}', input1=ctx))

        # Argument missing.
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=embed_error(f'You missed the `{error.param.name}` parameter for the command `{ctx.command}`. '
                                                    f'Use `{ctx.prefix}help {ctx.command}` for more information on what parameters to use.', input1=ctx))

        # Too many arguments.
        elif isinstance(error, commands.TooManyArguments):
            return await ctx.send(embed=embed_error(f'You are trying to use too many parameters for the command `{ctx.command}`. '
                                                    f'Use `{ctx.prefix}help {ctx.command}` for more information on what parameters to use.', input1=ctx))

        # Wrong argument.
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(embed=embed_error(f'I was not able to understand the parameter that you are trying to use for the command `{ctx.command}`. '
                                                    f'Use `{ctx.prefix}help {ctx.command}` for more information on what parameters to use.', input1=ctx))

        # Command only for servers.
        elif isinstance(error, commands.NoPrivateMessage):
            return await ctx.send(embed=embed_error(f'The command `{ctx.command}` is not avaiable in private messages. '
                                                    f'Use `{ctx.prefix}help {ctx.command}` for more information on how to use it.', input1=ctx))

        # Command only for owners.
        elif isinstance(error, commands.NotOwner):
            return await ctx.send(embed=embed_error(f'The command `{ctx.command}` is only avaiable for developer/owner. ', input1=ctx))

        #If it is a non-handled error we will pass the error message obtained.
        else:
            try:
                if hasattr(ctx.command, 'on_error'):
                    return
                else:
                    message = f'`{ctx.command.qualified_name} {ctx.command.signature}` \n{error}'
                    return await ctx.send(embed=embed_error(message, input1=ctx))
            except:
                message = f'{error}'
                return await ctx.send(embed=embed_error(message, input1=ctx, input2=error))
            
def setup(bot):
    bot.add_cog(ErrorCog(bot))
    message = 'Error Cog has been loaded succesfully.'
    print('• ' + f'{message}')
    bot.log.info(f'{message}')
       
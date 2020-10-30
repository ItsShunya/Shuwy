import discord
from discord.ext import commands
from utilities.embeds import embed_error, set_style

class ModerationCog(commands.Cog, name='Moderation'):
    '''Cog in charge of different moderation functions for servers.'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, *, number:int=None):
        '''Deletes the amount of messages introduced as parameter
        
        Keyword arguments:
        number -- number of messages to be deleted (default=None)  '''

        try:
            if number is None:
                message = 'You must input a number of messages to purge.'
                await ctx.send(embed=embed_error(message, input1=ctx))
            else:
                deleted = await ctx.message.channel.purge(limit=number)
                embed = discord.Embed(title=f'Purge has been completed by {ctx.message.author.mention}', description=f'{len(deleted)} messages have been deleted.', color=discord.Colour.purple())
                await ctx.send(embed=set_style(embed))
        except:
            message = 'I cannot purge messages here.'
            await ctx.send(embed=embed_error(message, input1=ctx))

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason='None'):
        '''Kicks the specified user from the current server.
        
        Keyword arguments:
        user -- user to be kicked
        reason -- message to be displayed as reason for the kick'''

        if user.guild_permissions.manage_messages:
            message = 'I cannot kick this user because they are an admin/moderator.'
            await ctx.send(embed=embed_error(message, input1=ctx))
        else:
            await ctx.guild.kick(user=user, reason=reason)
            embed = discord.Embed(title=f'{user} has been kicked by {ctx.message.author}', description=f'Reason: {reason}.', color=discord.Colour.purple())
            await ctx.send(embed=set_style(embed))
    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason='None'):
        '''Bans the specified user from the current server.
        
        Keyword arguments:
        user -- user to be banned
        reason -- message to be displayed as reason for the ban'''

        if user.guild_permissions.manage_messages:
            message = 'I cannot ban this user because they are an admin/moderator.'
            await ctx.send(embed=embed_error(message, input1=ctx))
        else:
            await ctx.guild.ban(user=user, reason=reason)
            embed = discord.Embed(title=f'{user} has been banned by {ctx.message.author}', description=f'Reason: {reason}.', color=discord.Colour.purple())
            await ctx.send(embed=set_style(embed))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.Member, *, reason='None'):
        '''Unbans the specified user from the current server.
        
        Keyword arguments:
        user -- user to be unbanned 
        reason -- message to be displayed as reason for the unban'''

        await ctx.guild.unban(user=user, reason=reason)
        embed = discord.Embed(title=f'{user} has been unbanned by {ctx.message.author}', description=f'Reason: {reason}.', color=discord.Colour.purple())
        await ctx.send(embed=set_style(embed))

    @commands.command()
    async def userinfo(self, ctx, *, member: discord.Member=None):
        '''Tells all the information about an user.

        Keyword arguments:
        user -- user to be investigated'''

        if member is None:
            member = ctx.author
        roles = [role for role in member.roles]
        embed = discord.Embed(color=discord.Colour.purple())
        embed.set_author(name=f'User Info - {member}')
        embed.add_field(name='ID:', value=member.id)
        embed.add_field(name='Server name:', value=member.display_name)
        embed.add_field(name='Created at:', value=member.created_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'))
        embed.add_field(name='Joined at:', value=member.joined_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'))
        embed.add_field(name=f'Roles ({len(roles)})', value=' '.join([role.mention for role in roles]))
        embed.add_field(name='Top role:', value=member.top_role.mention)
        embed.add_field(name='Bot?', value=member.bot)
        await ctx.send(embed=set_style(embed))

    async def cog_check(self, ctx: commands.Context):
        '''Cog wide check, which disallows commands in DMs.'''

        if not ctx.guild and '!help' not in ctx.message.content:
            embed = discord.Embed(description='Moderation commands are not available in Private Messages!', color=discord.Colour.purple())  
            await ctx.send(embed=set_style(embed))
            return False
        
        return True

def setup(bot):
    bot.add_cog(ModerationCog(bot))
    message = 'Moderation Cog has been loaded succesfully.'
    print('• ' + f'{message}')
    bot.log.info(f'{message}')
import sqlite3
import re
import os
import datetime
import discord
from discord.ext import commands
from utilities.embeds import *

database_path = os.path.join(f'{os.path.dirname(__file__)}', '../config', 'database.sqlite')

class MembersCog(commands.Cog, name='Members'):
    '''Cog in charge of the functions related to members, roles and permissions.'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='joined', aliases=['unido', 'entered'])
    async def joined(self, ctx, *, member: discord.Member=None):
        '''Says when a member joined.

        Keyword arguments:
        member -- member object that we want to check  '''

        if member is None:
            member = ctx.author
        embed = discord.Embed(color=discord.Colour.purple(), description=f'{member.display_name} joined on {member.joined_at}')
        await ctx.send(embed=set_style(embed))

    @commands.command(name='top_role', aliases=['toprole', 'top_rol', 'toprol'])
    async def show_toprole(self, ctx, *, member: discord.Member=None):
        '''Simple command which shows the members Top Role.
        
        Keyword arguments:
        member -- member object that we want to check  '''

        if member is None:
            member = ctx.author
        embed = discord.Embed(color=discord.Colour.purple(), description=f'The top role for {member.display_name} is {member.top_role.name}')
        await ctx.send(embed=set_style(embed))

    @commands.command(name='perms', aliases=['perms_for', 'permissions'])
    async def check_permissions(self, ctx, *, member: discord.Member=None):
        '''A simple command which checks a members Guild Permissions.
        If member is not provided, the author will be checked.
        
        Keyword arguments:
        member -- member object that we want to check  '''

        if not member:
            member = ctx.author
        # Here we check if the value of each permission is True.
        perms = '\n'.join(perm for perm, value in member.guild_permissions if value)
        # And to make it look nice, we wrap it in an Embed.
        embed = discord.Embed(title='Permissions for:', description=ctx.guild.name, colour=0xebb145)
        embed.set_author(icon_url=member.avatar_url, name=str(member))
        # \uFEFF is a Zero-Width Space, which basically allows us to have an empty field name.
        embed.add_field(name='\uFEFF', value=perms)
        await ctx.send(content=None, embed=set_style(embed))

    @commands.group(invoke_without_commands=True)
    async def welcome(self, ctx):
        '''Command to set the preferences for the welcome channel/message/role.
           Needs to be used together with one of its subcommands.'''

        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=discord.Colour.purple(), title='Available Commands:', description='welcome channel <#channel>\nwelcome text <message>\nwelcome role <@role>\nwelcome channel_on\nwelcome channel_off\nwelcome role_on\nwelcome role_off')
            await ctx.send(embed=set_style(embed))

    @welcome.command()
    async def channel(self, ctx, channel:discord.TextChannel):
        '''Subcommand for "welcome" function to set the welcome channel.
        
        Keyword arguments:
        channel -- channel to be used for welcome messages'''

        if ctx.message.author.guild_permissions.manage_messages:
            database = sqlite3.connect(database_path)
            cursor = database.cursor()
            cursor.execute(f"SELECT welcome_channel_id FROM database WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            sql = ("UPDATE database SET welcome_channel_id = ? WHERE guild_id = ?")
            val = (channel.id, ctx.guild.id)
            await ctx.send(f'Welcome Channel has been set to {channel.mention}')
            cursor.execute(sql, val)
            database.commit()
            cursor.close()
            database.close()
        else:
            await ctx.send(embed=embed_error('You do not have permissions to use this command. Contact an admin for more information.', input1=ctx))

    @welcome.command()
    async def text(self, ctx, *, text):
        '''Subcommand for "welcome" function to set the welcome message.
        
        Keyword arguments:
        text -- message to be used as welcome messages'''

        if ctx.message.author.guild_permissions.manage_messages:
            database = sqlite3.connect(database_path)
            cursor = database.cursor()
            print(os.getcwd())
            cursor.execute(f"SELECT welcome_msg FROM database WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            sql = ("UPDATE database SET welcome_msg = ? WHERE guild_id = ?")
            val = (text, ctx.guild.id)
            await ctx.send(f'Welcome Message has been set to `{text}`')
            cursor.execute(sql, val)
            database.commit()
            cursor.close()
            database.close()
        else:
            await ctx.send(embed=embed_error('You do not have permissions to use this command. Contact an admin for more information.', input1=ctx))

    @welcome.command()
    async def role(self, ctx, role:discord.Role):
        '''Subcommand for "welcome" function to set the welcome role.
        
        Keyword arguments:
        role -- role to be set to new server members'''

        if ctx.message.author.guild_permissions.manage_roles:
            database = sqlite3.connect(database_path)
            cursor = database.cursor()
            sql = ("UPDATE database SET welcome_role_id = ? WHERE guild_id = ?")
            val = (role.id, ctx.guild.id)
            await ctx.send(f'Welcome Role has been set to {role.mention}')
            cursor.execute(sql, val)
            database.commit()
            cursor.close()
            database.close()
        else:
            await ctx.send(embed=embed_error('You do not have permissions to use this command. Contact an admin for more information.', input1=ctx))

    @welcome.command()
    async def channel_on(self, ctx):
        '''Subcommand for "welcome" function to activate the welcome message.'''

        database = sqlite3.connect(database_path)
        cursor = database.cursor()
        sql = ("UPDATE database SET welcome_channel_on = ? WHERE guild_id = ?")
        val = (1, ctx.guild.id)
        cursor.execute(sql, val)
        await ctx.send('Welcome Channel has been activated.')
        database.commit()
        cursor.close()
        database.close()

    @welcome.command()
    async def channel_off(self, ctx):
        '''Subcommand for "welcome" function to deactivate the welcome message.'''

        database = sqlite3.connect(database_path)
        cursor = database.cursor()
        sql = ("UPDATE database SET welcome_channel_on = ? WHERE guild_id = ?")
        val = (0, ctx.guild.id)
        cursor.execute(sql, val)
        await ctx.send('Welcome Channel has been deactivated.')
        database.commit()
        cursor.close()
        database.close()

    @welcome.command()
    async def role_on(self, ctx):
        '''Subcommand for "welcome" function to activate the welcome role.'''

        database = sqlite3.connect(database_path)
        cursor = database.cursor()
        sql = ("UPDATE database SET welcome_role_on = ? WHERE guild_id = ?")
        val = (1, ctx.guild.id)
        cursor.execute(sql, val)
        await ctx.send('Welcome Role has been activated.')
        database.commit()
        cursor.close()
        database.close()

    @welcome.command()
    async def role_off(self, ctx):
        '''Subcommand for "welcome" function to deactivate the welcome role.'''

        database = sqlite3.connect(database_path)
        cursor = database.cursor()
        sql = ("UPDATE database SET welcome_role_on = ? WHERE guild_id = ?")
        val = (0, ctx.guild.id)
        cursor.execute(sql, val)
        await ctx.send('Welcome Role has been deactivated.')
        database.commit()
        cursor.close()
        database.close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        '''Event that takes places when a user joins a guild.
           Here we will read the database and assign the member the necessary settings. '''

        guild = member.guild
        database = sqlite3.connect(database_path)
        cursor = database.cursor()
        cursor.execute(f"SELECT welcome_channel_on FROM database WHERE guild_id = {guild.id}")
        result0 = cursor.fetchone()
        if result0[0] is 1:
            cursor.execute(f"SELECT welcome_channel_id FROM database WHERE guild_id = {guild.id}")
            result = cursor.fetchone()
            if result[0] is None:
                if guild.system_channel is not None:
                    sql = ("UPDATE database SET welcome_channel_id = ? WHERE guild_id = ?")
                    val = (guild.system_channel.id, guild.id)
                    cursor.execute(sql, val)
                    channel = discord.utils.get(guild.text_channels, id=guild.system_channel.id)
                    cursor.execute(f"SELECT welcome_msg FROM database WHERE guild_id = {guild.id}")
                    result1 = cursor.fetchone()
                    if result1[0] is None:
                        msg = 'Hello {mention}! Welcome to {guild}'
                        await channel.send(embed=embed_welcome(msg, member))
                    else:
                        await channel.send(embed=embed_welcome(str(result1[0]), member))
                else:
                    return
            else:
                channel = discord.utils.get(guild.text_channels, id=int(result[0]))
                cursor.execute(f"SELECT welcome_msg FROM database WHERE guild_id = {guild.id}")
                result1 = cursor.fetchone()
                if result1[0] is None:
                    msg = 'Hello {mention}! Welcome to {guild}'
                    await channel.send(embed=embed_welcome(msg, member))
                else:
                    await channel.send(embed=embed_welcome(str(result1[0]), member))
        cursor.execute(f"SELECT welcome_role_on FROM database WHERE guild_id = {guild.id}")
        result2 = cursor.fetchone()
        if result2[0] is 1:
            cursor.execute(f"SELECT welcome_role_id FROM database WHERE guild_id = {guild.id}")
            database.commit()
            result3 = cursor.fetchone()
            if result3[0] is None:
                role_Name = 'New Member'
                await guild.create_role(name=role_Name)
                role = discord.utils.get(guild.roles, name = role_Name)
                sql = ("UPDATE database SET welcome_role_id = ? WHERE guild_id = ?")
                val = (role.id, guild.id)
                cursor.execute(sql, val)
                database.commit()
                await member.add_roles(role)
            else:
                role = guild.get_role(role_id=int(result3[0]))
                await member.add_roles(role)
        database.commit()
        cursor.close()
        database.close()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        '''Event that takes places when a reaction is added to a message.'''

        database = sqlite3.connect(database_path)
        cursor = database.cursor()
        if '<:' in str(reaction.emoji):
            cursor.execute(f"SELECT emoji, role, message_id, channel_id FROM reaction WHERE guild_id = '{reaction.guild_id}' and message_id = '{reaction.message_id}' and emoji = '{reaction.emoji.id}'")
            result = cursor.fetchone()
            guild = self.bot.get_guild(reaction.guild_id)
            if str(reaction.emoji.id) in str(result[0]):
                on = discord.utils.get(guild.roles, id=int(result[1]))
                user = guild.get_member(reaction.user_id)
                await user.add_roles(on)
            else:
                return
        else:
            cursor.execute(f"SELECT emoji, role, message_id, channel_id FROM reaction WHERE guild_id = '{reaction.guild_id}' and message_id = '{reaction.message_id}' and emoji = '{reaction.emoji}'")
            result = cursor.fetchone()
            guild = self.bot.get_guild(reaction.guild_id)
            if result is not None:
                on = discord.utils.get(guild.roles, id=int(result[1]))
                user = guild.get_member(reaction.user_id)
                await user.add_roles(on)
            else:
                return
        database.commit()
        cursor.close()
        database.close()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction):
        '''Event that takes places when a reaction is deleted from a message.'''

        database = sqlite3.connect(database_path)
        cursor = database.cursor()
        if '<:' in str(reaction.emoji):
            cursor.execute(f"SELECT emoji, role, message_id, channel_id FROM reaction WHERE guild_id = '{reaction.guild_id}' and message_id = '{reaction.message_id}' and emoji = '{reaction.emoji.id}'")
            result = cursor.fetchone()
            guild = self.bot.get_guild(reaction.guild_id)
            if str(reaction.emoji.id) in str(result[0]):
                on = discord.utils.get(guild.roles, id=int(result[1]))
                user = guild.get_member(reaction.user_id)
                await user.remove_roles(on)
            else:
                return
        else:
            cursor.execute(f"SELECT emoji, role, message_id, channel_id FROM reaction WHERE guild_id = '{reaction.guild_id}' and message_id = '{reaction.message_id}' and emoji = '{reaction.emoji}'")
            result = cursor.fetchone()
            guild = self.bot.get_guild(reaction.guild_id)
            if result is not None:
                on = discord.utils.get(guild.roles, id=int(result[1]))
                user = guild.get_member(reaction.user_id)
                await user.remove_roles(on)
            else:
                return
        database.commit()
        cursor.close()
        database.close()

    @commands.command()
    async def role_add(self, ctx, channel:discord.TextChannel, messageid, emoji, role:discord.Role):
        '''Sets a role to be added to a user when he reacts to a pre-defined message with a pre-defined role.

        Keyword arguments:
        channel -- channel where the message is set
        messageid -- ID of the message where the bot will react
        emoji -- emoji to be used
        role -- role to be added to the user'''

        database = sqlite3.connect(database_path)
        cursor = database.cursor()
        cursor.execute(f"SELECT emoji, role, message_id, channel_id FROM reaction WHERE guild_id = '{ctx.message.guild.id}' and message_id = '{messageid}'")
        result = cursor.fetchone()
        if '<:' in emoji:
            emm = re.sub(':.*?', '', emoji).strip('<>')
            if result is None or str(message_id) not in str(result[3]):
                sql = ("INSERT INTO reaction(emoji, role, message_id, channel_id, guild_id) VALUES(?,?,?,?,?)")
                val = (emm, role.id, messageid, channel.id, ctx.guild.id)
                cursor.execute(sql, val)
                msg = await channel.fetch_message(messageid)
                em = self.bot.get_emoji(int(emm))
                await msg.add_reaction(em)
        else:
            if result is None or str(message_id) not in str(result[3]):
                sql = ("INSERT INTO reaction(emoji, role, message_id, channel_id, guild_id) VALUES(?,?,?,?,?)")
                val = (emoji, role.id, messageid, channel.id, ctx.guild.id)
                cursor.execute(sql, val)
                msg = await channel.fetch_message(messageid)
                await msg.add_reaction(emoji)
        database.commit()
        cursor.close()
        database.close()

    @commands.command()
    async def role_remove(self, ctx, messageid=None, emoji=None):
        '''Use it after using role_add to make the bot remove the emoji and stop adding the role to the person reacting to it.

        Keyword arguments:
        messageid -- ID of the message where the bot had reacted
        emoji -- emoji used'''

        database = sqlite3.connect(database_path)
        cursor = database.cursor()
        cursor.execute(f"SELECT emoji, role, message_id, channel_id FROM reaction WHERE guild_id = '{ctx.message.guild.id}' and message_id = '{messageid}'")
        result = cursor.fetchone()
        if '<:' in emoji:
            emm = re.sub(':.*?', '', emoji).strip('<>')
            if result is None:
                await ctx.send(embed=embed_error('That reaction was not found on that message.', input1=ctx))
            elif str(messageid) in str(result[2]):
                cursor.execute(f"DELETE FROM reaction WHERE guild_id = '{ctx.message.guild.id}' and message_id = '{messageid}' and emoji = '{emm}'")
                embed = discord.Embed(description='Reaction has been removed.', color=discord.Colour.purple())  
                await ctx.send(embed=set_style(embed))
            else:
                await ctx.send(embed=embed_error('That reaction was not found on that message.', input1=ctx))
        else:
            if result is None:
                await ctx.send(embed=embed_error('That reaction was not found on that message.', input1=ctx))
            elif str(messageid) in str(result[2]):
                cursor.execute(f"DELETE FROM reaction WHERE guild_id = '{ctx.message.guild.id}' and message_id = '{messageid}' and emoji = '{emoji}'")
                embed = discord.Embed(description='Reaction has been removed.', color=discord.Colour.purple())  
                await ctx.send(embed=set_style(embed))
            else:
                await ctx.send(embed=embed_error('That reaction was not found on that message.', input1=ctx))
        database.commit()
        cursor.close()
        database.close()

    async def cog_check(self, ctx: commands.Context):
        '''Cog wide check, which disallows commands in DMs.'''

        if not ctx.guild and '!help' not in ctx.message.content:
            await ctx.send('Member related commands are not available in Private Messages!')
            return False
        
        return True

def setup(bot):
    bot.add_cog(MembersCog(bot))
    message = 'Members Cog has been loaded succesfully.'
    print('• ' + f'{message}')
    bot.log.info(f'{message}')
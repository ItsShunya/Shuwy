import discord
import datetime

def embed_welcome(message, member):
    '''Sets the embed message specifically for welcome messages.'''

    guild = member.guild
    user = member.name
    mention = member.mention
    members = len(list(member.guild.members))
    embed = discord.Embed(color=0xebb145, description=message.format(members=members, mention=mention, user=user, guild=guild))
    embed.set_thumbnail(url=f'{member.avatar_url}')
    embed.set_author(name=f'{member.name}', icon_url=f'{member.avatar_url}')
    return set_style(embed)

def embed_error(message, **kwargs):
    '''Sets the embed message specifically for error messages.'''
    input1 = kwargs.get('input1')
    input2 = kwargs.get('input2')
    input3 = kwargs.get('input3')
    input4 = kwargs.get('input4')
    embed = discord.Embed(title=f'Error in command: {input1.command}', description=message, color=0xebb145)
    return set_style(embed)

def set_style(embed):
    '''Sets the style used for any kind of embed messages
       To be used in ALL embeds so they are displayed with the same style (thumbnail, footer, timestamp).'''
    embed.set_thumbnail(url='https://i.imgur.com/NYsLYRr.jpg')
    embed.set_footer(text = 'Developer/Owner: Shunya#1624 ', icon_url = 'https://yt3.ggpht.com/a/AATXAJwhPDl8XMKJJmXiBj-bsQFBDfEFluin0ywkZ66M=s100-c-k-c0xffffffff-no-rj-mo')
    embed.timestamp = datetime.datetime.utcnow()
    return embed
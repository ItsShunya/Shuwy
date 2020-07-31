import os
from os import system
import shutil
import asyncio
import discord
import youtube_dl
from discord.ext import commands
from cogs.utilities.embeds import embed_error, set_style

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

queues = {}
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': False,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }],
    'postprocessor_args': [
        '-ar', '16000'
    ],
    'prefer_ffmpeg': True,
}

ffmpeg_options = {
    'options': '-vn'
}

class MusicCog(commands.Cog, name='Music'):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def join(self, ctx, *, voice_channel: discord.VoiceChannel=None):
        """Says when a member joined."""
        if voice_channel is None:
            voice_channel = ctx.message.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await voice_channel.connect()

    @commands.command()
    async def leave(self, ctx):
        """Says when a member joined."""
        if ctx.voice_client is not None:
            return await ctx.message.guild.voice_client.disconnect(force=True)
        await ctx.send(embed=embed_error(f'I am not on any voice channel! '
                                         f'Use `{ctx.prefix}help {ctx.command}` for more information on how to use this command.', input1=ctx))

    @commands.command()
    async def play(self, ctx, url: str):
        name = None
        def check_queue():
            Queue_infile = os.path.isdir("./Queue")
            if Queue_infile is True:
                DIR = os.path.abspath(os.path.realpath("Queue"))
                length = len(os.listdir(DIR))
                still_q = length - 1
                try:
                    first_file = os.listdir(DIR)[0]
                except:
                    print("No more queued song(s)\n")
                    queues.clear()
                    return
                main_location = os.path.dirname(os.path.realpath(__file__))
                song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
                if length != 0:
                    print("Song done, playing next queued\n")
                    print(f"Songs still in queue: {still_q}")
                    song_there = os.path.isfile("song.mp3")
                    if song_there:
                        os.remove("song.mp3")
                    shutil.move(song_path, main_location)
                    for file in os.listdir("./"):
                        if file.endswith(".mp3"):
                            os.rename(file, 'song.mp3')

                    voice.play(discord.FFmpegPCMAudio("song.mp3", **ffmpeg_options), after=lambda e: check_queue())
                    voice.source = discord.PCMVolumeTransformer(voice.source)
                    voice.source.volume = 0.07

                else:
                    queues.clear()
                    return

            else:
                queues.clear()
                print("No songs were queued before the ending of the last song\n")

        song_there = os.path.isfile("song.mp3")
        try:
            if song_there:
                os.remove("song.mp3")
                queues.clear()
                print("Removed old song file")
        except PermissionError:
            print("Trying to delete song file, but it's being played")
            await ctx.send("ERROR: Music playing")
            return

        Queue_infile = os.path.isdir("./Queue")
        try:
            Queue_folder = "./Queue"
            if Queue_infile is True:
                print("Removed old Queue Folder")
                shutil.rmtree(Queue_folder)
        except:
            print("No old Queue folder")

        await ctx.send("Getting everything ready now")

        try:
            with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
                print("Downloading audio now\n")
                ydl.download([url])
        except:
            print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL)")
            c_path = os.path.dirname(os.path.realpath(__file__))
            system("spotdl -f " + '"' + c_path + '"' + " -s " + url)

        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                name = file
                print(f"Renamed File: {file}\n")
                os.rename(file, "song.mp3")
        if name is None:
            return await ctx.send(embed=embed_error(f'There was an error while processing the command `{ctx.command}`. '
                                                    f'It was not possible to load the song, please try again.', input1=ctx))
        ctx.voice_client.play(discord.FFmpegPCMAudio("song.mp3", **ffmpeg_options), after=lambda e: check_queue())
        ctx.voice_client.source = discord.PCMVolumeTransformer(ctx.voice_client.source)
        ctx.voice_client.source.volume = 0.09

        nname = name.rsplit("-", 2)
        await ctx.send(f"Playing: {nname[0]}")
        print("playing\n")

    @commands.command(aliases=['q', 'que'])
    async def queue(ctx, url: str):
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is False:
            os.mkdir("Queue")
        DIR = os.path.abspath(os.path.realpath("Queue"))
        q_num = len(os.listdir(DIR))
        q_num += 1
        add_queue = True
        while add_queue:
            if q_num in queues:
                q_num += 1
            else:
                add_queue = False
                queues[q_num] = q_num

        queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

        try:
            with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
                print("Downloading audio now\n")
                ydl.download([url])
        except:
            print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL)")
            q_path = os.path.abspath(os.path.realpath("Queue"))
            system(f"spotdl -f song{q_num} -f " + '"' + q_path + '"' + " -s " + url)


        await ctx.send("Adding song " + str(q_num) + " to the queue")

        print("Song added to queue\n")

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            print('Music has been stopped.')
            embed = discord.Embed(description=f'Music has been stopped by {ctx.author.mention}', color=0xffd500)  
            return await ctx.send(embed=set_style(embed))
        else:
            await ctx.send(embed=embed_error(f'There is no music playing, could not stop it. '
                                             f'Use `{ctx.prefix}help {ctx.command}` for more information on how to use this command.', input1=ctx))

    @commands.command()
    async def pause(self, ctx):
        """Stops and disconnects the bot from voice"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            print('Music has been paused.')
            embed = discord.Embed(description=f'Music has been paused by {ctx.author.mention}', color=0xffd500)  
            return await ctx.send(embed=set_style(embed))
        else:
            await ctx.send(embed=embed_error(f'There is no music playing, could not pause it. '
                                             f'Use `{ctx.prefix}help {ctx.command}` for more information on how to use this command.', input1=ctx))

    @commands.command()
    async def resume(self, ctx):
        """Stops and disconnects the bot from voice"""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            print('Music has been resumed')
            embed = discord.Embed(description=f'Music has been resumed by {ctx.author.mention}', color=0xffd500)  
            return await ctx.send(embed=set_style(embed))
        else:
            await ctx.send(embed=embed_error(f'The music is not paused, could not resume it. '
                                             f'Use `{ctx.prefix}help {ctx.command}` for more information on how to use this command.', input1=ctx))

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

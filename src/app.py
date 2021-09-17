from logging import exception
import youtube_dl
import discord
from discord.ext import commands
from discord.utils import get

import os

bot = commands.Bot(command_prefix = '>')

@bot.command(name = 'ping') # verifies that the bot is running
async def ping(ctx): 
    await ctx.send("pong!") 

@bot.command(name = 'play')
async def play(ctx):
    author_channel = ctx.message.author.voice.channel
    
    if not author_channel:
        await ctx.send("Tenés que conectarte a un canal de voz para poner musica wachin")
        return

    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(author_channel)
    else:
        voice = await author_channel.connect()


@bot.command(name = 'disc')
async def disc(ctx):
    author_channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild = ctx.guild)
    await voice.disconnect()


@bot.command(name = 'repr')
async def repr(ctx, url:str):
    active_song = os.path.isfile('song.mp3')
    try:
        if active_song:
            os.remove("song.mp3")
            print(f"song {active_song} removed")
    
    except PermissionError:
        print("Song reproducing...")
        await ctx.send("Ya hay una cancion reproduciendose") 
        return

    await ctx.send("Anda todo fresco :cold_face:")

    voice = get(bot.voice_clients, guild = ctx.guild)

    youtube_sound = {
        'format' : 'bestaudio/best',
        'postprocessor' : [{
            'key'              : 'FFmnegExtractAudio',
            'proferredcodec'   : 'mp3',
            'proferredquality' : '192'
        }] 
    }

    with youtube_dl.YoutubeDL(youtube_sound) as ydl:
        print("Downloading song...")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3") or file.endswith(".m4a"):
            name = file
            print(f"Renaming file: {file}")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after = lambda x: print("song finished"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.06

    song_name = name.rsplit("-", 2)

    await ctx.send(f"Ahora suena: {song_name[0]}") 


if __name__ == '__main__':
    print('Bot Corriendo!')
    bot.run(os.getenv("TOKEN"))
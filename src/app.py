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


@bot.command(name = 'play') # reproducir musica con el comando >play <song>
async def play(ctx, url:str): # Conectar el bot y reproducir una cancion
    author_channel = ctx.message.author.voice.channel
    
    if not author_channel: # Verificar que la persona que envio el comando este en un canal de voz
        await ctx.send("Tenés que conectarte a un canal de voz para poner musica wachin")
        return

    voice = get(bot.voice_clients, guild = ctx.guild) # comando que nos permite usar "la voz"

    if voice and voice.is_connected(): # ir al canal de voz del autor del mensaje que prendio el bot
        await voice.move_to(author_channel)
    else:
        voice = await author_channel.connect()

    # Aca termina de conectarse el bot y empieza con el proceso de reproducir musica

    active_song = os.path.isfile('song.mp3')

    try: # ir borrando las canciones a medida que se reproducen para limpiar espacio
        if active_song:
            os.remove("song.mp3")
            print(f"song {active_song} removed")
    
    except PermissionError:
        print("Song reproducing...")
        await ctx.send("Ya hay una cancion reproduciendose") 
        return

    await ctx.send("Anda todo fresco :cold_face:")

    youtube_sound = { # configuraciones de descarga del sonido
        'format' : 'bestaudio/best',
        'postprocessor' : [{
            'key'              : 'FFmnegExtractAudio',
            'proferredcodec'   : 'mp3',
            'proferredquality' : '192'
        }] 
    }

    with youtube_dl.YoutubeDL(youtube_sound) as ydl: # descargar la cancion del link
        print("Downloading song...")
        ydl.download([url])

    for file in os.listdir("./"): # renombrar la cancion a song.mp3
        if file.endswith(".mp3") or file.endswith(".m4a"):
            name = file
            print(f"Renaming file: {file}")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after = lambda x: print("song finished"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.06

    song_name = name.rsplit("-", 2)

    await ctx.send(f"Ahora suena: {song_name[0]}") 


@bot.command(name = 'pause')
async def pause(ctx):
    voice = get(bot.voice_clients, guild = ctx.guild) # comando que nos permite usar "la voz"

    if voice and voice.is_playing():
        print("Pause")
        voice.pause()
        await ctx.send("Musica pausada")
    
    else:
        print("Error pausing, nothing to pause")
        await ctx.send("No hay nada reproduciendose")


@bot.command(name = 'resume')
async def pause(ctx):
    voice = get(bot.voice_clients, guild = ctx.guild) # comando que nos permite usar "la voz"

    if voice and voice.is_paused():
        print("Resuming song")
        voice.resume()
        await ctx.send("Volvimo")
    
    else:
        print("Error resuming, nothing playing")
        await ctx.send("No hay nada pausado")


@bot.command(name = 'stop')
async def stop(ctx):
    voice = get(bot.voice_clients, guild = ctx.guild) # comando que nos permite usar "la voz"

    if voice and voice.is_playing():
        print("Stopping music")
        voice.stop()
        await ctx.send("Se detuvo la reproduccion")
    
    else:
        print("Error stopping, nothing playing")
        await ctx.send("No hay nada reproduciéndose")


@bot.command(name = 'disc') # desconectar el bot del canal de voz
async def disc(ctx):
    author_channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild = ctx.guild)
    await voice.disconnect()


if __name__ == '__main__':
    print('Bot Corriendo!')
    bot.run(os.getenv("TOKEN"))
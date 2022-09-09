#!/usr/bin/env python

import re
import random
import discord
import urllib.request
from unidecode import unidecode
from discord.ext import commands
from youtube_dl import YoutubeDL
from bot import MusicBot
import sys
import os

ERROR_EMOJIS = ['🙅‍♂️', '❌']

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.YDL_OPTIONS = {
            "format" : "bestaudio", 
            "noplaylist" : "True"
        }

        self.FFMPEG_OPTIONS = {
            "before_options" : "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options" : "-vn"
        }

        self.instances = []


    def search_youtube(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download = False)["entries"][0]
            except Exception:
                return False
        return {"source" : info["formats"][0]["url"], "title" : info["title"]}
    

    def fetch_next_video(self, artist_name : str):
        artist_name_for_url = re.sub(" ", "+", artist_name)
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=one+song+from" + str(artist_name_for_url))

        video_ids = re.findall(r"watch\?v=(\S{11})", unidecode(html.read().decode()))
        video_ids = self._remove_duplicates(video_ids)

        return "https://www.youtube.com/watch?v=" + random.choice(video_ids)


    def _remove_duplicates(self, urls : list):
        unique_urls = []
        [unique_urls.append(url) for url in urls if url not in unique_urls]
        return unique_urls


    def get_instance_by_voice_channel(self, voice_channel):
        for i in range(len(self.instances)):
            if self.instances[i].get_voice_channel() == voice_channel:
                return self.instances[i]

        instance = MusicBot(voice_channel)
        self.instances.append(instance)
        return instance


    def play_next(self, instance): 
        # this is a recursive function, after play a song, calls 
        # itself for playing the next song until the queue is empty
        
        if not instance.music_queue_is_empty():

            # get the first utl of the queue
            next_song = instance.get_next_song()

            song_url = next_song[0]["source"]

            if not instance.is_playing:
                instance.alternate_state()
                
            instance.get_voice_channel().play(discord.FFmpegPCMAudio(song_url, **self.FFMPEG_OPTIONS), after = lambda x: self.play_next(instance))

        else:  # If the queue if empty, add a new song to it
            next_song = self.fetch_next_video(instance.get_artist_playing())
            query = "".join(next_song)
            song = self.search_youtube(query)

            if not instance.is_playing:
                instance.alternate_state()

            instance.get_voice_channel().play(discord.FFmpegPCMAudio(song["source"], **self.FFMPEG_OPTIONS), after = lambda x: self.play_next(instance))
   
   
    async def play_music(self, ctx, instance):

        if not instance.music_queue_is_empty():
            next_song = instance.music_queue[0]
            song_url = next_song[0]["source"]

            # connect to voice chanel
            try:
                if not instance.get_voice_channel() or not instance.get_voice_channel().is_connected():
                    instance.voice_channel = await next_song[1].connect()
                else:
                    await instance.voice_channel.move_to(instance.music_queue[0][1])
            except:
                    instance.voice_channel = await next_song[1].connect()
                        
            # remove first element of the queue (currently playing)
            instance.set_current_song(instance.get_next_song())

            if not instance.is_playing:
                instance.alternate_state()

            instance.get_voice_channel().play(discord.FFmpegPCMAudio(song_url, **self.FFMPEG_OPTIONS), after = lambda x: self.play_next(instance))
        
        else:  # Add suggested song to the queue
            next_song = self.fetch_next_video(instance.get_artist_playing())  # Get song url from youtube (from the artist thats now playing)
            query = "".join(next_song)
            song = self.search_youtube(query) 

            voice_channel = ctx.author.voice.channel  # Get the voice channel of the user who called the command
            if type(song) == type(True):
                await ctx.message.add_reaction("🤨")
                await ctx.message.add_reaction("❔")
                await ctx.send("No pude encontrar la cancion")

            else:  # Add the song to the queue
                instance.add_to_queue([song, voice_channel])

                if not instance.is_playing:
                    instance.alternate_state()
                    await self.play_music(ctx)  # Play the song


    @commands.command(help = "Poner una canción")
    async def play(self, ctx, *args):
        query = " ".join(args)

        try:
            voice_channel = ctx.author.voice.channel  # Get the voice channel of the user who called the command
        except Exception as e:  # The user who called the bot must be connected to a voice channel
            await ctx.message.add_reaction('😠')
            await ctx.message.add_reaction('❌')
            await ctx.send("Pará un poco, tenes que estar conectado a un canal de voz para escuchar musica :triumph:")
            return

        try:
            song = self.search_youtube(query)
            instance = self.get_instance_by_voice_channel(voice_channel)
            instance.set_artist_playing(str(song['title'].split('-')))

            if type(song) == type(True):
                await ctx.message.add_reaction('😩')
                await ctx.send("No pude encontrar la cancion :pensive:")
                return
            
            else:
                await ctx.message.add_reaction('👍')
                await ctx.send("Cancion agregada a la cola 👌")
                instance.add_to_queue([song, voice_channel])

                try:
                    if not instance.is_playing:
                        await self.play_music(ctx, instance)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno, e)

        except Exception as e:
            print(e)
            await ctx.message.add_reaction('🤣')
            await ctx.message.add_reaction('👆')
            await ctx.send("Che que me pasaste? :flushed: Tenés que usar >play nombre-del-tema para poner una canción")
            return

        
    @commands.command(aliases = ["aver", "cola"], help = "Ver las canciones agregadas a la cola")
    async def queue(self, ctx):  # Show the queue in a message
        await ctx.message.add_reaction("🧐")

        try:
            instance = self.get_instance_by_voice_channel(ctx.author.voice.channel)
        except:
            await ctx.message.add_reaction("😐")
            await ctx.send("Vos me estás cargando? No hay ningún canal de voz para que consultes la cola :face_with_raised_eyebrow:")

        queue = instance.get_music_queue()

        retval = ""
        for i in range(len(queue)):
            retval += queue[i][0]["title"] + "\n"
        
        if retval:
            await ctx.send(retval)
        
        else:
            await ctx.send("Nop, nada por acá")
        

    @commands.command(aliases = ["next", "siguiente", "omitir"], help = "Pasar a la siguiente canción")
    async def skip(self, ctx):  # Skip to the next song
        instance = self.get_instance_by_voice_channel(ctx.author.voice.channel)
        if ctx.author.voice.channel:  # The user who called the bot must be connected to a voice channel
            instance.get_voice_channel().stop()
            await self.play_music(ctx)
            await ctx.message.add_reaction("🥴")
            await ctx.message.add_reaction("⏭️")
            return
        
        await ctx.message.add_reaction("🤦‍♂️")
        await ctx.send("Te puedo preguntar que estás intentando skippear? :thinking:")


    @commands.command(aliases = ["p" "pausa", "pausar", "stop"], help = "Pausar")
    async def pause(self, ctx):
        ctx.author.voice.channel.pause()
        await ctx.message.add_reaction("😤")
        await ctx.message.add_reaction("✋")


    @commands.command(aliases = ["r", "seguir", "dale"], help = "Reanudar musica")
    async def resume(self, ctx):
        ctx.author.voice.channel.resume()
        await ctx.message.add_reaction("😌")
        await ctx.message.add_reaction("🫱")
        

    @commands.command(aliases = ["disc"], help = "Desconectar bot")
    async def disconnect(self, ctx):
        await ctx.message.add_reaction("👋")
        await ctx.author.voice.channel.disconnect()
        

    @commands.command(aliases = ["playing", "sonando"], help = "Mostrar canción sonando")
    async def show_current_song(self, ctx):
        complementary_emojis = ["🤓", "😄", "😎", "🤪", "💃", "🕺", "🎶"]
        try:
            await ctx.message.add_reaction("🔍")
            await ctx.message.add_reaction("👀")
            await ctx.send(f"{self.current_song[0]['title']} {random.choice(complementary_emojis)}")
        except:
            await ctx.send("¿Cuál está sonando? Buena pregunta. :thinking:")


    @commands.command(aliases = ["cambiar"], help = "Cambiar canción que está sonando actualmente")
    async def change(self, ctx, *args):
        query = " ".join(args)
        song = self.search_youtube(query)

        if type(song) == type(True):
            await ctx.message.add_reaction("😩")
            await ctx.send("No pude encontrar la cancion :pensive:")
            return
        
        else:
            instance = self.get_instance_by_voice_channel(ctx.author.voice.channel)
            instance.set_current_song([song, instance.get_voice_channel()])
            instance.agregar_cancion_colada(instance.get_current_song())
            await ctx.message.add_reaction("😈")
            await ctx.message.add_reaction("🎶")
            await ctx.send("Cambiando canción :smirk::ok_hand:")
            await self.skip(ctx)

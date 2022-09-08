#!/usr/bin/env python

import re
import random
import discord
import urllib.request
from unidecode import unidecode
from discord.ext import commands
from youtube_dl import YoutubeDL

ERROR_EMOJIS = ['🙅‍♂️', '❌']

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # music related values
        self.is_playing = False
        self.music_queue = []
        
        self.YDL_OPTIONS = {
            "format" : "bestaudio", 
            "noplaylist" : "True"
        }

        self.FFMPEG_OPTIONS = {
            "before_options" : "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options" : "-vn"
        }

        self.vc = None
        self.artist_playing = "harry styles" 


    def search_youtube(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download = False)["entries"][0]
            except Exception:
                return False
        return {"source" : info["formats"][0]["url"], "title" : info["title"]}
    

    def play_next(self): 
        # this is a recursive function, after play a song, calls 
        # itself for playing the next song until the queue is empty
        self.is_playing = True 
        if len(self.music_queue) > 0:

            # get the first utl of the queue
            song_url = self.music_queue[0][0]["source"]

            # remove currently playing song
            self.current_song = self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(song_url, **self.FFMPEG_OPTIONS), after = lambda x: self.play_next())

        else:  # If the queue if empty, add a new song to it
            next_song = self.fetch_next_video(self.artist_playing)
            query = "".join(next_song)
            song = self.search_youtube(query)

            print(song["source"])
            self.vc.play(discord.FFmpegPCMAudio(song["source"], **self.FFMPEG_OPTIONS), after = lambda x: self.play_next())
              

    async def play_music(self, ctx):

        if len(self.music_queue) > 0:
            song_url = self.music_queue[0][0]["source"]

            # connect to voice chanel
            if (self.vc == "") or (not self.vc.is_connected()) or (not self.vc):
                self.vc = await self.music_queue[0][1].connect()

            else:
                await self.vc.move_to(self.music_queue[0][1])
                        
            # remove first element of the queue (currently playing)
            self.current_song = self.music_queue.pop(0)

            self.is_playing = True
            self.vc.play(discord.FFmpegPCMAudio(song_url, **self.FFMPEG_OPTIONS), after = lambda x: self.play_next())
        
        else:  # Add suggested song to the queue
            next_song = self.fetch_next_video(self.artist_playing)  # Get song url from youtube (from the artist thats now playing)
            query = "".join(next_song)
            song = self.search_youtube(query) 

            voice_channel = ctx.author.voice.channel  # Get the voice channel of the user who called the command
            if type(song) == type(True):
                await ctx.message.add_reaction("🤨")
                await ctx.message.add_reaction("❔")
                await ctx.send("No pude encontrar la cancion")

            else:  # Add the song to the queue
                self.music_queue.append([song, voice_channel])

                if not self.is_playing:
                    self.is_playing = True
                    await self.play_music(ctx)  # Play the song
    

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


    @commands.command(help = "Poner una canción")
    async def play(self, ctx, *args):
        query = " ".join(args)

        try:
            voice_channel = ctx.author.voice.channel  # Get the voice channel of the user who called the command
        except Exception as e:  # The user who called the bot must be connected to a voice channel
            print(e)
            await ctx.message.add_reaction('😠')
            await ctx.message.add_reaction('❌')
            await ctx.send("Pará un poco, tenes que estar conectado a un canal de voz para escuchar musica :triumph:")
            return

        try:
            song = self.search_youtube(query)
            self.artist_playing = str(song['title'].split('-'))

            if type(song) == type(True):
                await ctx.message.add_reaction('😩')
                await ctx.send("No pude encontrar la cancion :pensive:")
                return
            
            else:
                await ctx.message.add_reaction('👍')
                await ctx.send("Cancion agregada a la cola 👌")
                self.music_queue.append([song, voice_channel])

                if not self.is_playing:
                    await self.play_music(ctx)
        
        except:
            await ctx.message.add_reaction('🤣')
            await ctx.message.add_reaction('👆')
            await ctx.send("Che que me pasaste? :flushed: Tenés que usar >play nombre-del-tema para poner una canción")
            return

        
    @commands.command(aliases = ["aver", "cola"], help = "Ver las canciones agregadas a la cola")
    async def queue(self, ctx):  # Show the queue in a message
        await ctx.message.add_reaction("🧐")

        retval = ""
        for i in range(len(self.music_queue)):
            retval += self.music_queue[i][0]["title"] + "\n"
        
        print(retval)
        if retval != "":
            await ctx.send(retval)
        
        else:
            await ctx.send("Nop, nada por acá")
        

    @commands.command(aliases = ["next", "siguiente", "omitir"], help = "Pasar a la siguiente canción")
    async def skip(self, ctx):  # Skip to the next song

        if self.vc != "" and self.vc:
            self.vc.stop()
            # play next in queue if exist
            await self.play_music(ctx)
            await ctx.message.add_reaction("🥴")
            await ctx.message.add_reaction("⏭️")


    @commands.command(aliases = ["p" "pausa", "pausar", "stop"], help = "Pausar")
    async def pause(self, ctx):
        self.vc.pause()
        await ctx.message.add_reaction("😤")
        await ctx.message.add_reaction("✋")


    @commands.command(aliases = ["r", "seguir", "dale"], help = "Reanudar musica")
    async def resume(self, ctx):
        self.vc.resume()
        await ctx.message.add_reaction("😌")
        await ctx.message.add_reaction("🫱")
        

    @commands.command(aliases = ["disc"], help = "Desconectar bot")
    async def disconnect(self, ctx):
        await ctx.message.add_reaction("👋")
        await self.vc.disconnect()
        

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
            self.current_song = [song, self.vc]
            self.music_queue.insert(0, self.current_song)
            await ctx.message.add_reaction("😈")
            await ctx.message.add_reaction("🎶")
            await ctx.send("Cambiando canción :smirk::ok_hand:")
            await self.skip(ctx)

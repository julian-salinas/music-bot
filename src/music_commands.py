import discord
from discord.ext import commands

from youtube_dl import YoutubeDL

from fetch_next_video import fetch_next_video

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # music related values
        self.is_playing = False
        self.music_queue = []
        
        self.YDL_OPTIONS = {
            'format' : 'bestaudio', 
            'noplaylist' : 'True'
        }

        self.FFMPEG_OPTIONS = {
            'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options' : '-vn'
        }

        self.vc = ''
        self.artist_playing = 'harry styles'


    def search_youtube(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download = False)['entries'][0]
            except Exception:
                return False
        return {'source' : info['formats'][0]['url'], 'title' : info['title']}
    

    def play_next(self): 
        # this is a recursive function, after play a song, calls 
        # itself for playing the next song until the queue is empty
        self.is_playing = True 
        if len(self.music_queue) > 0:

            # get the first utl of the queue
            song_url = self.music_queue[0][0]['source']

            # remove currently playing song
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(song_url, **self.FFMPEG_OPTIONS), after = lambda x: self.play_next())

        else:  # If the queue if empty, add a new song to it
            next_song = fetch_next_video(self.artist_playing)
            query = "".join(next_song)
            song = self.search_youtube(query)

            print(song['source'])
            self.vc.play(discord.FFmpegPCMAudio(song['source'], **self.FFMPEG_OPTIONS), after = lambda x: self.play_next())
              

    async def play_music(self, ctx):
        self.is_playing = True

        if len(self.music_queue) > 0:
            song_url = self.music_queue[0][0]['source']

            # connect to voice chanel
            if (self.vc == "") or (not self.vc.is_connected()) or (not self.vc):
                self.vc = await self.music_queue[0][1].connect()

            else:
                await self.vc.move_to(self.music_queue[0][1])
                        
            # remove first element of the queue (currently playing)
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(song_url, **self.FFMPEG_OPTIONS), after = lambda x: self.play_next())
        
        else:  # Add suggested song to the queue
            next_song = fetch_next_video(self.artist_playing)  # Get song url from youtube (from the artist thats now playing)
            query = "".join(next_song)
            song = self.search_youtube(query) 

            voice_channel = ctx.author.voice.channel  # Get the voice channel of the user who called the command
            if type(song) == type(True):
                 await ctx.send("No pude encontrar la cancion :(")

            else:  # Add the song to the queue
                self.music_queue.append([song, voice_channel])

                if not self.is_playing:
                    await self.play_music(ctx)  # Play the song
    

    @commands.command(help = "Poner una canción")
    async def play(self, ctx, *args):
        query = " ".join(args)

        try:
            voice_channel = ctx.author.voice.channel  # Get the voice channel of the user who called the command
        except Exception as e:  # The user who called the bot must be connected to a voice channel
            print(e)
            await ctx.send("Pará un poco, tenes que estar conectado a un canal de voz para escuchar musica :triumph:")

        try:
            song = self.search_youtube(query)
            self.artist_playing = str(song['title'].split('-'))

            if type(song) == type(True):
                await ctx.send("No pude encontrar la cancion :pensive:")
            
            else:
                await ctx.send("Cancion agregada a la cola")
                self.music_queue.append([song, voice_channel])

                if not self.is_playing:
                    await self.play_music(ctx)
        
        except:
            await ctx.message.add_reaction('🤣')
            await ctx.message.add_reaction('👆')
            await ctx.send("Che que me pasaste? :flushed: Tenés que usar >play nombre-del-tema para poner una canción")


        
    @commands.command(aliases = ['aver', 'cola'], help = "Ver las canciones agregadas a la cola")
    async def queue(self, ctx):  # Show the queue in a message
        retval = ""
        for i in range(len(self.music_queue)):
            retval += self.music_queue[i][0]['title'] + "\n"
        
        print(retval)
        if retval != "":
            await ctx.send(retval)
        
        else:
            await ctx.send("No hay canciones agregadas a la cola")
        

    @commands.command(aliases = ['next', 'siguiente', 'omitir'], help = "Pasar a la siguiente canción")
    async def skip(self, ctx):  # Skip to the next song

        if self.vc != "" and self.vc:
            self.vc.stop()
            # play next in queue if exist
            await self.play_music(ctx)


    @commands.command(aliases = ['p' 'pausa', 'pausar', 'stop'], help = "Pausar")
    async def pause(self, ctx):
        self.vc.pause()


    @commands.command(aliases = ['r', 'seguir', 'dale'], help = "Reanudar musica")
    async def resume(self, ctx):
        self.vc.resume()


    @commands.command(aliases = ['disc'], help = "Desconectar bot")
    async def disconnect(self, ctx):
        await self.vc.disconnect()
        
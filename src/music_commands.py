import discord
from discord import voice_client
from discord.ext import commands
from discord.utils import get

from youtube_dl import YoutubeDL

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

        self.voice_channel = ''

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
        if len(self.music_queue) > 0:
            self.is_playing = True

            # get the first utl of the queue
            song_url = self.music_queue[0][0]['source']

            # remove currently playing song
            self.music_queue.pop(0)

            self.voice_channel.play(discord.FFmpegPCMAudio(song_url, **self.FFMPEG_OPTIONS), after = lambda x: self.play_next())

        else:
            self.is_playing = False
    

    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            song_url = self.music_queue[0][0]['source']

            # connect to voice chanel
            if self.voice_channel == "" or not self.voice_channel.is_connected():
                self.voice_channel = await self.music_queue[0][1].connect()

            else:
                self.voice_channel = await self.bot.move_to(self.music_queue[0][1])
                        
            # remove first element of the queue (currently playing)
            self.music_queue.pop(0)

            self.voice_channel.play(discord.FFmpegPCMAudio(song_url, **self.FFMPEG_OPTIONS), after = lambda x: self.play_next())
        
        else:
            self.is_playing = False
    

    @commands.command()
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if not voice_channel:  
            # the person who sent the command must be in a voice channel
            await ctx.send("Para un toque, tenes que estar conectado a un canal de voz para escuchar musica")

        else:
            song = self.search_youtube(query)
            if type(song) == type(True):
                await ctx.send("No pude encontrar la cancion :(")
            
            else:
                await ctx.send("Cancion agregada a la cola (tuya)")
                self.music_queue.append([song, voice_channel])

                if not self.is_playing:
                    await self.play_music()
                
        
    @commands.command()
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += self.music_queue[i][0]['title'] + "\n"
        
        print(retval)
        if retval != "":
            await ctx.send(retval)
        
        else:
            await ctx.send("No music in queue")
        

    @commands.command()
    async def next(self, ctx):
        if self.voice_channel != "":
            self.voice_channel.stop()
            # play next in queue if exist
            await self.play_music()


    @commands.command()
    async def pausar(self, ctx):
        self.voice_channel.pause()


    @commands.command()
    async def seguir(self, ctx):
        self.voice_channel.resume()


    @commands.command()
    async def help_pls(self, ctx):
        output = '''
        *Comandos disponibles del bot:*
        **/play** `<nombre de la cancion o link de youtube>` → Poner un tema
        **/queue** → Ver todos los temas que tenés en la cola
        **/next** → Pasar al siguiente tema
        **/pausar** → adivina
        **/seguir** → Reanudar musica
        '''
        await ctx.send(output)
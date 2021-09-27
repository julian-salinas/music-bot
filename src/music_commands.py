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

        self.vc = ''

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

            self.vc.play(discord.FFmpegPCMAudio(song_url, **self.FFMPEG_OPTIONS), after = lambda x: self.play_next())

        else:
            self.is_playing = False
    

    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            song_url = self.music_queue[0][0]['source']

            # connect to voice chanel
            if (self.vc == "") or (not self.vc.is_connected()) or (not self.vc):
                self.vc = await self.music_queue[0][1].connect()

            else:
                await self.vc.move_to(self.music_queue[0][1])
                        
            # remove first element of the queue (currently playing)
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(song_url, **self.FFMPEG_OPTIONS), after = lambda x: self.play_next())
        
        else:
            self.is_playing = False
    

    @commands.command(help = "-play <nombre de la cancion o url en youtube> para tocar una cancion")
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
                
        
    @commands.command(help = "Ver las canciones que tenés en la cola")
    async def queue(self, ctx):
        retval = ""
        for i in range(len(self.music_queue)):
            retval += self.music_queue[i][0]['title'] + "\n"
        
        print(retval)
        if retval != "":
            await ctx.send(retval)
        
        else:
            await ctx.send("Tenés la cola vacía")
        

    @commands.command(aliases = ['next'], help = "Pasar a la siguiente canción")
    async def skip(self, ctx):
        if self.vc != "" and self.vc:
            self.vc.stop()
            # play next in queue if exist
            await self.play_music()


    @commands.command(aliases = ['p'], help = "Pausar")
    async def pause(self, ctx):
        self.vc.pause()


    @commands.command(aliases = ['r'], help = "Reanudar musica")
    async def resume(self, ctx):
        self.vc.resume()


    @commands.command()
    async def help_pls(self, ctx):
        output = '''
        *Comandos disponibles del bot:*
        **/play** `<nombre de la cancion o link de youtube>` → Poner un tema
        **/queue** → Ver todos los temas que tenés en la cola
        **/next** → Pasar al siguiente tema
        **/p** → adivina
        **/r** → Reanudar musica
        '''
        await ctx.send(output)


    @commands.command(aliases = ['disc'], help = "Desconectar bot")
    async def disconnect(self, ctx):
        await self.vc.disconnect()
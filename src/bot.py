import discord
from discord.ext import commands

from music_commands import MusicCog

TOKEN = "ODg4MzA1NzA5NjM5NDA1NTc5.YUQxKQ.5f-wv--V3Phzclvuo0k8Z2e8sDQ"

Bot = commands.Bot(command_prefix = '/')

Bot.add_cog(MusicCog(Bot))


if __name__ == '__main__':
    print("Bot corriendoououo!")
    Bot.run(TOKEN)
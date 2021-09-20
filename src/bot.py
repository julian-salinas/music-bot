import os
import discord
from discord.ext import commands

from music_commands import MusicCog

Bot = commands.Bot(command_prefix = '/')

Bot.add_cog(MusicCog(Bot))

if __name__ == '__main__':
    print("Bot corriendoououo!")
    Bot.run((os.getenv('TOKEN')))
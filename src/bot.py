import os
import discord
from discord.ext import commands

from music_commands import MusicCog

Bot = commands.Bot(command_prefix = '/')

Bot.add_cog(MusicCog(Bot))

TOKEN="ODg4MzA1NzA5NjM5NDA1NTc5.YUQxKQ.hWiQx8n9F46Lc7znPTO1WmupCXg"

if __name__ == '__main__':
    print("Bot corriendoououo!")
    Bot.run(TOKEN)
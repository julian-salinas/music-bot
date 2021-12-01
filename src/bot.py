import os
from dotenv import load_dotenv
from discord.ext import commands
import discord

from music_commands import MusicCog


load_dotenv()


Bot = commands.Bot(command_prefix = '>')


Bot.add_cog(MusicCog(Bot))

@Bot.event
async def on_ready():
    await Bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="MOGUS"))

if __name__ == '__main__':
    print("Bot corriendo!")
    Bot.run(os.getenv('TOKEN'))

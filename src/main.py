#!/usr/bin/env python

import os
import discord
from discord.ext import commands
from music_commands import MusicCog

grubi = commands.Bot(command_prefix = ">")

grubi.add_cog(MusicCog(grubi))

@grubi.event
async def on_ready():
    await grubi.change_presence(activity = discord.Activity(type = discord.ActivityType.playing, name = "MOGUS"))

if __name__ == "__main__":
    print("Bot corriendo!")
    grubi.run(os.getenv("TOKEN"))

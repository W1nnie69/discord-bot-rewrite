import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import config


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), application_id = 887197279386214480)


@bot.event
async def on_ready():
    print("online")

    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")



bot.run(config.token)
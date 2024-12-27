import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import config


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), application_id = 887197279386214480, help_command=None)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    option = input("Load test or live: ")
    if option == "test":
        await bot.load_extension("cogs.testing_cog")

    else:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")


    # Sync commands
    print("Commands have been synced.")


bot.run(config.token)
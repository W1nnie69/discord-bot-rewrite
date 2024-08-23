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



async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


async def main():
    await load()
    await bot.start(config.token)



# Command to sync slash commands (optionally for a specific guild)
# @bot.command()
# async def sync(ctx, guild_id: int = None):
#     if guild_id:
#         guild = discord.Object(id=guild_id)
#         synced = await bot.tree.sync(guild=guild)
#         await ctx.send(f"Synced {len(synced)} command(s) to guild {guild_id}.")
#     else:
#         synced = await bot.tree.sync()
#         await ctx.send(f"Synced {len(synced)} command(s) globally.")


asyncio.run(main())
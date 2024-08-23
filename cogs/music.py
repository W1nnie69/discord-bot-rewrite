import discord
from discord.ext import commands
from discord import app_commands

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("music cog loaded")


    @commands.command()
    async def sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(fmt)} commands.")
        

    @app_commands.command(name = "ping", description = "testing")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong")

    # async def cog_load(self):
    #     guild_id = 1259846523626197043  # Replace with your server's ID or set to None for global
    #     guild = discord.Object(id=guild_id) if guild_id else None
    #     await self.bot.tree.sync(guild=guild)

async def setup(bot):
    await bot.add_cog(Music(bot), guilds=[discord.Object(id=1259846523626197043)])
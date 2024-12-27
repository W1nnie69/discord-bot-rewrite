import discord
from discord.ext import commands, tasks
import asyncio
import yt_dlp
from discord import Color
import time
from youtube_search import YoutubeSearch
import json
from icecream import ic
import json_handling as jshand



class testing_cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.command()
    async def test(self, ctx, *, query):

        links = ["http://", "https://", "www."]

        try: 
            if any(link in query for link in links):
                print("link")
                await ctx.send(query)

            else:
                print("normal query")
                await ctx.send(query)

        except:
            await ctx.send("Unknown error occured. Try again")


        print("function end")



async def setup(bot):
    await bot.add_cog(testing_cog(bot))
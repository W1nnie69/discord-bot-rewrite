import discord
from discord.ext import commands
from discord.utils import get
import asyncio


class Troll(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.wanted = False



    @commands.command()
    async def qegq803r03u9b39tub9ubu31t03ub1t(self, ctx):
        member = ctx.author
        guild = ctx.guild   
        role = guild.get_role(1313845262300479519)
        await member.add_roles(role)
        await ctx.message.delete()



    async def arrLoop(self, member, channel):
        while True:
            if self.wanted == True:
                await member.move_to(channel)
                print("looping")
                await asyncio.sleep(0.5)

            else:
                return



    @commands.command()
    async def arrest(self, ctx, member: discord.Member):
        channel = self.bot.get_channel(1325395744718454855)
        
        self.wanted = True
        if self.wanted == True:
            self.bot.loop.create_task(self.arrLoop(member, channel))
        
        else:
            pass



    @commands.command()
    async def release(self, ctx):
        self.wanted = False







async def setup(bot):
    await bot.add_cog(Troll(bot))
import discord
from discord.ext import commands
import asyncio
import yt_dlp
from discord import Color
import time
from youtube_search import YoutubeSearch
import json
from icecream import ic
import json_handling as jshand



class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.song_queue = {}
        self.current_song = {}
        self.yt_sqtitle = []
        self.yt_cstitle = []
        self.check_song_queue = []
        self.check_current_song = []

        self.loop_current_song = False
        self.queue_is_looping = False
        self.loop = False


    @commands.Cog.listener()
    async def on_ready(self):
        print("music cog loaded")



    async def join_channel(self, ctx):
        channel = ctx.author.voice.channel
        await channel.connect()


    
    async def say_q_empty(self, ctx):
        await ctx.send(f"Queue is empty")




    def play_next(self, ctx):
        
    # If looping, play the same song again
        if self.loop_current_song:
            # checks if there is a song in current_song
            if self.current_song:
                # Takes song from current_song and plays it
                loop1_url = self.current_song[0]
                self.bot.loop.create_task(self.play_youtube(ctx, loop1_url))
            
            else: # In case if current_song is empty and loop is enabled
                # adds the first song in song_queue to current_song
                self.current_song.append(self.song_queue[0])

                # Takes song from current_song and plays it
                loop2_url = self.current_song[0]     
                self.bot.loop.create_task(self.play_youtube(ctx, loop2_url))

        # When not looping current song
        elif not self.loop_current_song:

            if self.queue_is_looping:
                
                if self.current_song:
                    
                    self.song_queue.append(self.current_song[0])
                    self.current_song.clear()
                    self.current_song.append(self.song_queue[0])     
                    url = self.song_queue.pop(0)
                    self.bot.loop.create_task(self.play_youtube(ctx, url))

                if not self.current_song:

                    self.yt_title.pop(0)
                    # adds first song in song_queue to current_song (for when loop is applied when the current song is playing)
                    self.current_song.append(self.song_queue[0])
                    # Takes first song in song_queue and plays it while removing it from the list
                    url = self.song_queue.pop(0)
                    self.bot.loop.create_task(self.play_youtube(ctx, url))

            elif self.song_queue:
                ic(self.song_queue)
                self.current_song.clear()
                self.current_song = self.song_queue
                ic(self.current_song)
                # url = self.song_queue.pop(0)
                self.bot.loop.create_task(self.play_youtube(ctx))


            else:
                # For when queue is empty
                voice_channel = ctx.voice_client
                if voice_channel.is_playing():
                    time.sleep(1)

                else:
                    self.bot.loop.create_task(self.say_q_empty(ctx))
                    self.current_song.clear()




    async def play_youtube(self, ctx):

        ydl_opts = {
        'format': 'bestaudio/best',
        # 'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        }

        url = self.current_song['link']

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=False)
            url2 = info['url']

            voice_channel = ctx.voice_client
            voice_channel.stop()

            FFMPEG_OPTIONS = {
            'executable': 'ffmpeg.exe',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }   

            voice_channel.play(discord.FFmpegOpusAudio(url2, **FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))

            # await ctx.send(f"Now playing: {info['title']}")
            # await interaction.response.send_message(f"Now playing: {info['title']}")
            
            # self.yt_title.append(info['title'])

        # return info['title']





    # @commands.command()
    # async def sync(self, ctx, global_sync: bool = False) -> None:
    #     if global_sync:
    #         # Sync commands globally
    #         fmt = await self.bot.tree.sync()
    #         await ctx.send(f"Synced {len(fmt)} global commands.")
    #     else:
    #         # Sync commands for the guild
    #         fmt = await self.bot.tree.sync(guild=ctx.guild)
    #         await ctx.send(f"Synced {len(fmt)} guild commands.")
        



    # @commands.command()
    # async def clear_global_commands(self, ctx):
    #     global_commands = await self.bot.tree.fetch_commands()
    #     for command in global_commands:
    #         await self.bot.tree.delete_command(command.id)
    #     await ctx.send("All global commands have been cleared.")
        



    # @commands.command()
    # async def desync(self, ctx) -> None:
    #     ctx.bot.tree.clear_commands(guild=ctx.guild)
    #     await ctx.send("Local commands have been cleared.")



    @commands.command(name="ping", description="testing")
    async def ping(self, ctx):
        await ctx.send("pong")




    @commands.command(name='join', description='join user channel')
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        if not ctx.voice_client:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)
        





    @commands.command(name='leave', description='leaves the channel')
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
        




    @commands.command(name='play', description='plays youtube links')
    async def play(self, ctx, url):

        # Check if the bot is already connected to a voice channel
        if ctx.voice_client is None:
        # If not connected, join the voice channel
            await self.join_channel(ctx)

        self.song_queue.append(url)

        if not ctx.voice_client.is_playing():
            self.play_next(ctx)

            #todo: fix the stupid title thing
        




    @commands.command(name='skip', description='skips the current song')
    async def skip(self, ctx):
        voice_channel = ctx.voice_client
        if voice_channel and voice_channel.is_playing():
            voice_channel.stop()

        self.play_next(ctx)
        





    
    @commands.command(name='stop', description='Stops the current song')
    async def stop(self, ctx):
        voice_channel = ctx.voice_client
        if voice_channel and voice_channel.is_playing():
            voice_channel.stop()
            self.current_song.clear()
            self.song_queue.clear()
        
        #fix stop as it works like skip LOL





    @commands.command(name='loop', description='Loops the current song')
    async def loop(self, ctx):

        self.loop_current_song = not self.loop_current_song
        await ctx.send(f"Looping current song: {self.loop_current_song}")




    @commands.command(name='loop_q', description='Loops the whole queue')
    async def loop_q(self, ctx):
        self.queue_is_looping = not self.queue_is_looping

        if self.queue_is_looping == True:
            await ctx.send(f"Looping the queue")

        else:
            await ctx.send(f"Not looping the queue")






    @commands.command(name='queue', description='Shows the song queue')
    async def queue(self, ctx):
    
        yellow = Color.yellow()

        embed_songtitle = discord.Embed(
            title='Queue list',
            colour=yellow
        )

        # cs = self.current_song
        # sq = self.song_queue
        
        # print(cs)
        # print(sq)

        # self.check_current_song
        ic(self.current_song)
        ic(self.song_queue)
        print("")
        ic(self.check_current_song)
        ic(self.check_song_queue)

        if self.check_current_song != self.current_song:

            self.check_current_song.clear()
            self.check_song_queue.clear()
            self.yt_cstitle.clear()
            self.yt_sqtitle.clear()

            with yt_dlp.YoutubeDL() as ydl_q:
                
                self.check_current_song = self.current_song.copy()
                self.check_song_queue = self.song_queue.copy()


                for i in self.check_current_song:
                    info_cs = ydl_q.extract_info(i, download=False)
                    info_cs = info_cs.get('title', None)
                    self.yt_cstitle.append(info_cs)
                    print(info_cs)

                for i in self.check_song_queue:
                    info_sq = ydl_q.extract_info(i, download=False)
                    info_sq = info_sq.get('title', None)
                    self.yt_sqtitle.append(info_sq)
                    print(info_sq)

        
        ic(self.current_song)
        ic(self.song_queue)
        print("")
        ic(self.check_current_song)
        ic(self.check_song_queue)



        cs_title = '\n'.join(self.yt_cstitle)

        sq_title = '\n'.join(self.yt_sqtitle)

        embed_songtitle.add_field(name='Current Song', value=cs_title, inline=False)

        embed_songtitle.add_field(name='Queue', value=sq_title, inline=False)

        await ctx.send(embed=embed_songtitle)






    @commands.command(name='find', description='find a song/video on youtube')
    async def find(self, ctx, *, query: str):

        result_dict = {}
        # title_dict = []
        # a = 0

        results = YoutubeSearch(query, max_results=10).to_dict()
        for index, v in enumerate(results, start=1):
            # a = a + 1  

            link = 'https://www.youtube.com/watch?v=' + v['id']
            title = v['title']

            result_dict[str(index)] = {"title": title, "link": link}
            # yt_title = v['title']
            
            # title_dict.append(v)



        with open("temp-ytlist.json", "w") as outfile: 
            json.dump(result_dict, outfile, indent=4)

        # for i in range(1,11):
        #     msg = dict1[i]

        # numbered_links = [f"{idx}) {data['title']}: {data['link']}" for idx, data in result_dict.items()]
        # numbered_links_str = '\n'.join(numbered_links)
        emtitle = []

        for i in result_dict: #for the embed
            emtitle.append(f"{i}) {result_dict[i]['title']}")

        emtitle = '\n'.join(emtitle)

        yellow = Color.yellow()


        embed_find = discord.Embed(
            title=f'Search Results: "{query}" ',
            colour=yellow
        )


        embed_find.add_field(name='title', value=emtitle, inline=False)


        await ctx.send(embed=embed_find)
            



    @commands.command(name='op', description='options for /find')
    async def op(self, ctx, *, value: str):
        

        channel = ctx.author.voice.channel
        
        with open("temp-ytlist.json", "r") as file:
            data = json.load(file)


        title = data[value]['title']
        link = data[value]['link']
        
        
        jshand.rmJsonVal()

        # self.song_queue.append(link)

        self.song_queue = {'title':title, 'link':link}

        ic(self.song_queue)

        if not ctx.voice_client:
            await self.join_channel(ctx)

        if not ctx.voice_client.is_playing():
            self.play_next(ctx)

        await ctx.send(f"Option {value} selected!")



    @commands.command(name='test', description='testing')
    async def test(self, ctx):
        # await interaction.response.send_message("testingsrufbg")
        await ctx.send("testing baslls")



   
async def setup(bot):
    await bot.add_cog(Music(bot))
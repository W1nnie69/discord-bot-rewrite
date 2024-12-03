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

        self.song_queue = []
        self.current_song = []

        self.loop_current_song = False
        self.queue_is_looping = False



    @commands.Cog.listener()
    async def on_ready(self):
        print("music cog loaded")



    async def join_channel(self, ctx):
        channel = ctx.author.voice.channel
        await channel.connect()


    
    async def say_q_empty(self, ctx):
        await ctx.send(f"Queue is empty")




    def play_next(self, ctx):
        if self.song_queue:


            if not self.queue_is_looping:
        

                if not self.loop_current_song:
                    #default behaviour, no loops--------------------------------------

                    if self.current_song: #checks if current_song is empty, if not it will clear it
                        self.current_song.clear()

                    # self.current_song = self.song_queue.popitem()
                
                    self.current_song = self.song_queue.pop(0)

                    self.bot.loop.create_task(self.play_youtube(ctx))

                    
                else:
                    #if current song is LOOPING---------------------------------------
                    if self.current_song: #checks if current_song is empty, if not it will clear it
                        self.bot.loop.create_task(self.play_youtube(ctx))
                        

                    else:
                        #If current song is empty
                        self.current_song = self.song_queue.pop(0)
                        self.bot.loop.create_task(self.play_youtube(ctx))
                        
            
            else:
                #if QUEUE is looping--------------------------------------------------

                #check if there is value in current_song
                if self.current_song: #checks if current_song is empty, if not it will add it back to the queue
                    self.song_queue.append(self.current_song.copy())
                    self.current_song.clear()

                    # Takes first song in song_queue and returns it to current_song while removing it from the song_queue
                    self.current_song = self.song_queue.pop(0) 

                    self.bot.loop.create_task(self.play_youtube(ctx))

                else:
                    #If current_song is empty
                    self.current_song = self.song_queue.pop(0)
                    self.bot.loop.create_task(self.play_youtube(ctx))
                

        else:

            if self.loop_current_song:
                #check if loop_current_song is true--------------------------------------
                if self.current_song:
                #if loop current_song is enable and only 1 song was added,
                #making song_queue empty
                    self.bot.loop.create_task(self.play_youtube(ctx))

            else:
                #song_queue is empty
                self.bot.loop.create_task(self.say_q_empty(ctx))



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

            await ctx.send(f"Now playing: {info['title']}")
            # await interaction.response.send_message(f"Now playing: {info['title']}")
            
            # self.yt_title.append(info['title'])

        # return info['title']




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


        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            title = info['title']


        self.song_queue.append({'title':title, 'link':url})

        if not ctx.voice_client.is_playing():
            self.play_next(ctx)

            #todo: fix the stupid title thing
        




    @commands.command(name='skip', description='skips the current song')
    async def skip(self, ctx):
        voice_channel = ctx.voice_client
        if voice_channel and voice_channel.is_playing():
            voice_channel.stop()

        # self.play_next(ctx)
        





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

        if self.loop_current_song == True:
            self.queue_is_looping == False
            await ctx.send(f"Looping current song")

        else:
            await ctx.send(f"Stopping loop")




    @commands.command(name='loop_q', description='Loops the whole queue')
    async def loop_q(self, ctx):
        self.queue_is_looping = not self.queue_is_looping

        if self.queue_is_looping == True:
            self.loop_current_song = False
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

       
        cs_title = self.current_song['title']

        embed_songtitle.add_field(name='Current Song', value=cs_title, inline=False)


        sq_title = []

        for title in self.song_queue:
            sq_title.append(title['title'])

        if sq_title:
        
            index = 0

            sq_title_with_index = []

            for titles in sq_title:
                index = index + 1
                sq_title_with_index.append(f"{index}) " + titles)
                print(sq_title_with_index)


            sq_title_with_index_and_bracket_removed = '\n'.join(sq_title_with_index)

            embed_songtitle.add_field(name='Queue', value=sq_title_with_index_and_bracket_removed, inline=False)

            await ctx.send(embed=embed_songtitle)

        else:
            embed_songtitle.add_field(name='Queue', value="Empty", inline=False)

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
 
                           # title = 0     link = 1
        self.song_queue.append({'title':title, 'link':link})


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
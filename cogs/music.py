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


    
    async def auto_disconnect(self, ctx):
        voice_channel = ctx.voice_client
        if voice_channel:
            if not voice_channel.is_playing():

                for _ in range(60): #Time in seconds
                    if voice_channel.is_playing():
                        return
                    
                    else:
                        await asyncio.sleep(1)

                voice_channel.stop()
                await ctx.voice_client.disconnect()



    @commands.command(name="help", description="Bot help page")
    async def help(self, ctx):
        yellow = Color.yellow()

        embed_helppage = discord.Embed(
            title="Help page",
            colour=yellow
        )

        play =  "!play <yt link/yt title>        | Plays yt links or searches a yt video by putting in title (remove <> when typing commands)"
        op =    "!op <number>                    | Select a song/vid from the search results of !play"
        skip =  "!skip                           | To skip the current song/vid."
        stop =  "!stop                           | To stop the bot completely, clearing the queue."
        loop =  "!loop                           | Repeats the current song indefinitely until the user types the command again to disable looping."
        loopq = "!loopq                          | Repeats the whole queue + current song/vid indefinitely until the user types the command again to disable looping."
        queue = "!queue                          | Displays the current song and the upcoming songs in the queue."
        joincmd  = "!join                           | Makes the bot join the voice channel you're currently in."
        leave = "!leave                          | Disconnects the bot from the current voice channel."

    

        embed_helppage.add_field(name="Commands", value=play, inline=False)
        embed_helppage.add_field(name="", value=op, inline=False)
        embed_helppage.add_field(name="", value=skip, inline=False)
        embed_helppage.add_field(name="", value=stop, inline=False)
        embed_helppage.add_field(name="", value=loop, inline=False)
        embed_helppage.add_field(name="", value=loopq, inline=False)
        embed_helppage.add_field(name="", value=queue, inline=False)
        embed_helppage.add_field(name="", value=joincmd, inline=False)
        embed_helppage.add_field(name="", value=leave, inline=False)

        await ctx.send(embed=embed_helppage)



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
                self.current_song.clear()
                self.bot.loop.create_task(self.say_q_empty(ctx))
                self.bot.loop.create_task(self.auto_disconnect(ctx))



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

        try:
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

        except Exception as e:
            ctx.send("Error downloading video. \n Video might be age-restricted.")
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




    @commands.command(name='loopq', description='Loops the whole queue')
    async def loopq(self, ctx):
        self.queue_is_looping = not self.queue_is_looping

        if self.queue_is_looping == True:
            self.loop_current_song = False
            await ctx.send(f"Looping the queue")

        else:
            await ctx.send(f"Not looping the queue")




    @commands.command(name='play', description='plays youtube links')
    async def play(self, ctx, *, query: str):

        # Check if the bot is already connected to a voice channel
        if ctx.voice_client is None:
        # If not connected, join the voice channel
            try:
                await self.join_channel(ctx)

            except:
                await ctx.send("Join a channel first dumbass")
                return


        links = ["http://", "https://", "www."]

        try: 
            if any(link in query for link in links):  #for yt links
                print("link")
                
                with yt_dlp.YoutubeDL() as ydl:
                    info = ydl.extract_info(query, download=False)
                    title = info['title']

                if self.current_song:
                    await ctx.send("Song added to queue!")
                                   
                self.song_queue.append({'title':title, 'link':query})

                if not ctx.voice_client.is_playing():
                    self.play_next(ctx)

            else:
                print("normal query") #for yt searches
                result_dict = {}
                
                results = YoutubeSearch(query, max_results=10).to_dict()
                for index, v in enumerate(results, start=1):

                    link = 'https://www.youtube.com/watch?v=' + v['id']
                    title = v['title']

                    result_dict[str(index)] = {"title": title, "link": link}
                    
                with open("temp-ytlist.json", "w") as outfile: 
                    json.dump(result_dict, outfile, indent=4)

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



        except Exception as e:
            await ctx.send("Unknown error occured. Try again")
            print(f"Error: {e}")


    



    @commands.command(name='queue', description='Shows the song queue')
    async def queue(self, ctx):
    
        if not self.current_song:
            if not self.song_queue:
                await ctx.send("The Queue is empty dumbass")
                return

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




   
async def setup(bot):
    await bot.add_cog(Music(bot))
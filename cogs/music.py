import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp
from discord import Color
import time
from icecream import ic
from youtube_search import YoutubeSearch
import json



class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        print("music cog loaded")


    song_queue = []
    current_song = []
    yt_sqtitle = []
    yt_cstitle = []
    check_song_queue = []
    check_current_song = []

    loop_current_song = False
    queue_is_looping = False
    loop = False


    async def rmJsonVal(self):
        with open("temp-ytlist.json", "r") as file:
            data = json.load(file)

        for i in range(1,11):
            data.pop(str(i))

        with open("temp-ytlist.json", "w") as file2:
            json.dump(data, file2, indent=4)





    def play_next(self, interaction):
        
    # If looping, play the same song again
        if self.loop_current_song:
            # checks if there is a song in current_song
            if self.current_song:
                # Takes song from current_song and plays it
                loop1_url = self.current_song[0]
                self.bot.loop.create_task(self.play_youtube(interaction, loop1_url))
            
            else: # In case if current_song is empty and loop is enabled
                # adds the first song in song_queue to current_song
                self.current_song.append(self.song_queue[0])

                # Takes song from current_song and plays it
                loop2_url = self.current_song[0]     
                self.bot.loop.create_task(self.play_youtube(interaction, loop2_url))

        # When not looping current song
        elif not self.loop_current_song:

            if self.queue_is_looping:
                
                if self.current_song:
                    
                    self.song_queue.append(self.current_song[0])
                    self.current_song.clear()
                    self.current_song.append(self.song_queue[0])     
                    url = self.song_queue.pop(0)
                    self.bot.loop.create_task(self.play_youtube(interaction, url))

                if not self.current_song:

                    self.yt_title.pop(0)
                    # adds first song in song_queue to current_song (for when loop is applied when the current song is playing)
                    self.current_song.append(self.song_queue[0])
                    # Takes first song in song_queue and plays it while removing it from the list
                    url = self.song_queue.pop(0)
                    self.bot.loop.create_task(self.play_youtube(interaction, url))

            elif self.song_queue:

                self.current_song.clear()
                self.current_song.append(self.song_queue[0])
                url = self.song_queue.pop(0)
                self.bot.loop.create_task(self.play_youtube(interaction, url))


            else:
                # For when queue is empty
                voice_channel = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
                if voice_channel.is_playing():
                    time.sleep(1)

                else:
                    self.current_song.clear()




    async def play_youtube(self, interaction, url):

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

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=False)
            url2 = info['url']

            voice_channel = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
            voice_channel.stop()

            FFMPEG_OPTIONS = {
            'executable': 'ffmpeg.exe',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }   

            voice_channel.play(discord.FFmpegOpusAudio(url2, **FFMPEG_OPTIONS), after=lambda e: self.play_next(interaction))

            # await ctx.send(f"Now playing: {info['title']}")
            # await interaction.response.send_message(f"Now playing: {info['title']}")
            
            # self.yt_title.append(info['title'])

        # return info['title']





    @commands.command()
    async def sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(fmt)} commands.")
        



    @app_commands.command(name="ping", description="testing")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong")




    @app_commands.command(name='join', description='join user channel')
    async def join(self, interaction: discord.Interaction):
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message("I'm coming daddy")





    @app_commands.command(name='leave', description='leaves the channel')
    async def leave(self, interaction: discord.Interaction):
        vc = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        await vc.disconnect()
        await interaction.response.send_message("Bye Daddy")




    @app_commands.command(name='play', description='plays youtube links')
    async def play(self, interaction: discord.Interaction, link: str):

        channel = interaction.user.voice.channel
        vc = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        await interaction.response.send_message("Yessir")

        if vc is None:
            await channel.connect()

        self.song_queue.append(link)

        # with yt_dlp.YoutubeDL() as ydl:
            
        #     info = ydl.extract_info(link, download=False)
        #     v_title = info.get('title', None)
        #     self.yt_title.append(v_title)
        #     print(v_title)

        if not interaction.guild.voice_client.is_playing():
            self.play_next(interaction)

            #todo: fix the stupid title thing
        






    @app_commands.command(name='skip', description='skips the current song')
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_channels

        if vc and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()


        await interaction.response.send_message("Skipped!")
        





    
    @app_commands.command(name='stop', description='Stops the current song')
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_channels
        await interaction.response.defer()

        if vc and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            self.current_song.clear()
            self.song_queue.clear()

        await interaction.followup.send("Bot Stopped!")
        
        #fix stop as it works like skip LOL





    @app_commands.command(name='loop', description='Loops the current song')
    async def loop(self, interaction: discord.Interaction):

        self.loop_current_song = not self.loop_current_song
        await interaction.response.send_message("Looping current song")




    @app_commands.command(name='loop_q', description='Loops the whole queue')
    async def loop_q(self, interaction: discord.Interaction):
        self.queue_is_looping = not self.queue_is_looping

        if self.queue_is_looping == True:
            await interaction.response.send_message("Looping the queue")

        else:
            await interaction.response.send_message("Not looping the queue")





    @app_commands.command(name='queue', description='Shows the song queue')
    async def queue(self, interaction: discord.Interaction):

        await interaction.response.defer()

        yellow = Color.yellow()

        embed_songtitle = discord.Embed(
            title='Queue list',
            colour=yellow,
        )

        # cs = self.current_song
        # sq = self.song_queue
        
        # print(cs)
        # print(sq)

        # self.check_current_song
        ic("before if check", self.current_song)
        ic("before if check", self.song_queue)
        print("")
        ic("before if check", self.check_current_song)
        ic("before if check", self.check_song_queue)
        print("")

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

        await interaction.followup.send(embed=embed_songtitle)






    @app_commands.command(name='find', description='find song')
    async def find(self, interaction: discord.Interaction, query: str):

        await interaction.response.defer()

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

        for i in result_dict:
            emtitle.append(f"{i}) {result_dict[i]['title']}")

        emtitle = '\n'.join(emtitle)


        embed_find = discord.Embed(
            title='Search Results'
        )


        embed_find.add_field(name='title', value=emtitle, inline=False)


        await interaction.followup.send(embed=embed_find)
            



    @app_commands.command(name='op', description='options for /find')
    async def op(self, interaction: discord.Interaction, value: str):
        await interaction.response.defer()

        channel = interaction.user.voice.channel
        vc = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        with open("temp-ytlist.json", "r") as file:
            data = json.load(file)

        link = data[value]['link']
        
        await self.rmJsonVal()

        self.song_queue.append(link)

        if vc is None:
            await channel.connect()

        if not interaction.guild.voice_client.is_playing():
            self.play_next(interaction)

        await interaction.followup.send("ok boss")



    @commands.command(name='test', description='testing')
    async def test(self, ctx):
        # await interaction.response.send_message("testingsrufbg")
        await ctx.send("testing baslls")



   
async def setup(bot):
    await bot.add_cog(Music(bot), guilds=[discord.Object(id=718052721751752776)])
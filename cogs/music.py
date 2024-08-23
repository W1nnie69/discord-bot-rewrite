import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        print("music cog loaded")


    song_queue = []
    current_song = []
    loop_current_song = False
    queue_is_looping = False
    loop = False



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
                    asyncio.sleep(1)

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
            
        return info['title']





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

        if not interaction.guild.voice_client.is_playing():
            self.play_next(interaction)
        


    @app_commands.command(name='skip', description='skips the current song')
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_channels
        await interaction.response.defer()

        if vc and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()


        await interaction.followup.send("Skipped!")
        self.play_next(interaction)



    
    @app_commands.command(name='stop', description='Stops the current song')
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_channels
        await interaction.response.defer()

        if vc and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            self.current_song.clear()

        await interaction.followup.send("Bot Stopped!")
    



    @app_commands.command(name='loop', description='Loops the current song')
    async def loop(self, interaction: discord.Interaction):

        self.loop_current_song = not self.loop_current_song
        await interaction.response.send_message("Looping cuurent song")






    @commands.command(name='test', description='testing')
    async def test(self, ctx):
        # await interaction.response.send_message("testingsrufbg")
        await ctx.send("testing baslls")



   
async def setup(bot):
    await bot.add_cog(Music(bot), guilds=[discord.Object(id=1259846523626197043)])
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
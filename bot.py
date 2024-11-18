import discord
from discord.ext import commands
import yt_dlp as youtube_dl
from discord import app_commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

queue = []
last_played_song = None

@bot.tree.command(name="join", description="Make the bot join your voice channel.")
async def join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("You need to join a voice channel first!")
        return

    channel = interaction.user.voice.channel
    try:
        await channel.connect()
        await interaction.response.send_message(f"Joined {channel.name}!")
    except discord.errors.ClientException as e:
        await interaction.response.send_message(f"Failed to join the voice channel: {str(e)}")

@bot.tree.command(name="play", description="Play a song from YouTube in a voice channel.")
async def play(interaction: discord.Interaction, song: str):
    """Plays a song from YouTube in a voice channel."""
    
    await interaction.response.defer()

    if not interaction.user.voice:
        await interaction.followup.send("You need to join a voice channel first!")
        return

    channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client

    if voice_client:
        if voice_client.channel != channel:
            await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'extractaudio': True,
        'audioquality': 1,
        'outtmpl': 'downloads/%(id)s.%(ext)s',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{song}", download=False)
            url2 = info['entries'][0]['url']
            song_name = info['entries'][0]['title']
        except Exception as e:
            await interaction.followup.send(f"Could not find the song: {e}")
            return

    queue.append((song_name, url2))
    
    if not voice_client.is_playing():
        await play_next(voice_client, interaction)

    await interaction.followup.send(f"Added to queue: {song_name}")

async def play_next(voice_client, interaction):
    """Plays the next song in the queue."""
    if queue:
        song_name, url = queue.pop(0)
        voice_client.play(discord.FFmpegPCMAudio(url), after=lambda e: on_song_end(e, voice_client, interaction))
        await interaction.channel.send(f"Now playing: {song_name}")  # Send the song name

        global last_played_song
        last_played_song = (song_name, url)

def on_song_end(error, voice_client, interaction):
    """Handles the end of a song."""
    if error:
        print(f"Error: {error}")
    if queue:
        bot.loop.create_task(play_next(voice_client, interaction))
    else:
        print("Queue is empty, nothing more to play.")
        if not voice_client.is_playing():
            bot.loop.create_task(voice_client.disconnect())

@bot.tree.command(name="stop", description="Stop the music and leave the voice channel.")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        queue.clear()
        await interaction.response.send_message("Disconnected and stopped the music.")
    else:
        await interaction.response.send_message("I'm not connected to a voice channel.")

@bot.tree.command(name="pause", description="Pause the current song.")
async def pause(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await interaction.response.send_message("The song has been paused.")
    else:
        await interaction.response.send_message("No song is currently playing.")

@bot.tree.command(name="resume", description="Resume the paused song.")
async def resume(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("The song has been resumed.")
    else:
        await interaction.response.send_message("No song is currently paused.")

@bot.tree.command(name="queue", description="Shows the current song queue.")
async def queue_list(interaction: discord.Interaction):
    if queue:
        queue_str = "\n".join([f"{i+1}. {song_name}" for i, (song_name, _) in enumerate(queue)])
        await interaction.response.send_message(f"Current queue:\n{queue_str}")
    else:
        await interaction.response.send_message("The queue is empty.")

@bot.tree.command(name="skip", description="Skip to the next song in the queue.")
async def skip(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()  # Stop the current song
        await interaction.response.send_message("Song skipped.")
        if queue:
            await play_next(voice_client, interaction)
        else:
            await interaction.response.send_message("No more songs in the queue.")
    else:
        await interaction.response.send_message("No song is currently playing.")

@bot.tree.command(name="loop", description="Loop the last played song.")
async def loop(interaction: discord.Interaction):
    if last_played_song:
        song_name, url = last_played_song
        queue.append((song_name, url))  # Add the last song back to the queue
        await interaction.response.send_message(f"Looping: {song_name}")
    else:
        await interaction.response.send_message("No song has been played yet to loop.")

@bot.tree.command(name="delqueue", description="Delete the entire song queue.")
async def delqueue(interaction: discord.Interaction):
    queue.clear()
    await interaction.response.send_message("The song queue has been cleared.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()
    print("Slash commands synced!")

bot.run('')

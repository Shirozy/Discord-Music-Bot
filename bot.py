import discord
from discord.ext import commands
import yt_dlp as youtube_dl
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

queue = []
last_played_song = None

@bot.event
async def on_voice_state_update(member, before, after):
    # If the bot leaves the voice channel or disconnects
    if member == bot.user and before.channel is not None and after.channel is None:
        print(f"Bot disconnected from {before.channel.name}, attempting to reconnect...")
        # Optionally, try to reconnect or clean up the queue if necessary
        await reconnect_to_voice_channel(before.channel)
        
async def reconnect_to_voice_channel(channel):
    if not bot.voice_clients or bot.voice_clients[0].channel != channel:
        try:
            await channel.connect()
            print(f"Reconnected to {channel.name}")
        except discord.errors.ClientException as e:
            print(f"Failed to reconnect: {e}")
    else:
        print(f"Bot is already connected to {channel.name}. No need to reconnect.")


@bot.event
async def on_disconnect():
    print("Bot disconnected from the server. Reconnecting...")
    try:
        # Attempt to reconnect
        if bot.guilds:
            for guild in bot.guilds:
                for vc in guild.voice_clients:
                    if not vc.is_connected():
                        channel = vc.channel if vc else None
                        if channel:
                            await channel.connect()
                        break
    except Exception as e:
        print(f"Failed to reconnect: {e}")

@bot.tree.command(name="join", description="Make the bot join your voice channel.")
async def join(interaction: discord.Interaction):
    try:
        await interaction.response.send_message("🌟 I'm thinking... Let me check if you're in a voice channel! 🌟", ephemeral=True)

        if not interaction.user.voice:
            await interaction.followup.send("💔 Oops! You need to join a voice channel first! 💔", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.followup.send(embed=discord.Embed(
            title="Joined Channel!",
            description=f"🎧 Now I'm here in {channel.name}! Let's make some music! 🎶",
            color=discord.Color.green()
        ))

    except discord.errors.ClientException as e:
        await interaction.followup.send(f"😢 Failed to join the voice channel: {str(e)}", ephemeral=True)

@bot.tree.command(name="play", description="Play a song from YouTube in a voice channel.")
async def play(interaction: discord.Interaction, song: str):
    try:
        await interaction.response.defer()  # Defer the response

        if not interaction.user.voice:
            await interaction.followup.send("💔 You need to join a voice channel first! 💔", ephemeral=True)
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
                print(f"Playing song: {song_name} ({url2})")
            except Exception as e:
                await interaction.followup.send(f"💥 Oops! Couldn't find that song: {str(e)} 💥", ephemeral=True)
                return

        queue.append((song_name, url2))

        if not voice_client.is_playing():
            await play_next(voice_client, interaction)

        await interaction.followup.send(embed=discord.Embed(
            title="🎉 Added to Queue!",
            description=f"✅ **{song_name}** has been added to the queue! 🎶",
            color=discord.Color.blue()
        ))

    except Exception as e:
        await interaction.followup.send(f"💥 Something went wrong while trying to play the song: {str(e)} 💥", ephemeral=True)

async def play_next(voice_client, interaction):
    try:
        if queue:
            song_name, url = queue.pop(0)
            voice_client.play(discord.FFmpegPCMAudio(url), after=lambda e: on_song_end(e, voice_client, interaction))
            await interaction.channel.send(embed=discord.Embed(
                title="🎧 Now Playing!",
                description=f"🎶 **{song_name}** is now playing! Enjoy! 🎤\n🎧 - Check out the [Source]({url})",
                color=discord.Color.green()
            ))

            global last_played_song
            last_played_song = (song_name, url)
        else:
            await interaction.channel.send("🎉 No more songs in the queue, the party's over! 🎉")
            if voice_client.is_playing():
                voice_client.stop()

    except Exception as e:
        print(f"Error playing song: {e}")
        await interaction.channel.send("💥 Something went wrong while playing the song! 😔", embed=discord.Embed(color=discord.Color.red()))
        if queue:
            await play_next(voice_client, interaction)

def on_song_end(error, voice_client, interaction):
    if error:
        print(f"Error: {error}")
    
    if voice_client and voice_client.is_connected():
        if queue:
            bot.loop.create_task(play_next(voice_client, interaction))
        else:
            print("Queue is empty, nothing more to play.")
            if not voice_client.is_playing():
                bot.loop.create_task(voice_client.disconnect())

@bot.tree.command(name="stop", description="Stop the music and leave the voice channel.")
async def stop(interaction: discord.Interaction):
    try:
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            queue.clear()
            await interaction.response.send_message(embed=discord.Embed(
                title="❌ Music Stopped!",
                description="The music has been stopped, and I’m leaving the voice channel. Goodbye! 👋",
                color=discord.Color.red()
            ))
        else:
            await interaction.response.send_message("😞 I'm not connected to a voice channel to stop music. 😞", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"💥 Something went wrong while stopping: {str(e)} 💥", ephemeral=True)

@bot.tree.command(name="skip", description="Skip to the next song in the queue.")
async def skip(interaction: discord.Interaction):
    try:
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()  # Stop the current song
            await interaction.response.send_message("⏭️ Song skipped! Moving on to the next one! 🎶")
            if queue:
                await play_next(voice_client, interaction)
            else:
                await interaction.followup.send("🎉 No more songs in the queue, the party's over! 🎉")
        else:
            await interaction.response.send_message("😞 No song is currently playing to skip. 😞", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"💥 Something went wrong while skipping the song: {str(e)} 💥", ephemeral=True)

@bot.tree.command(name="pause", description="Pause the current song.")
async def pause(interaction: discord.Interaction):
    try:
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message(embed=discord.Embed(
                title="⏸️ Music Paused",
                description="The song has been paused! You can resume it later. 🎶",
                color=discord.Color.orange()
            ))
        else:
            await interaction.response.send_message("😞 No song is currently playing to pause. 😞", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"💥 Something went wrong while pausing the song: {str(e)} 💥", ephemeral=True)

@bot.tree.command(name="resume", description="Resume the paused song.")
async def resume(interaction: discord.Interaction):
    try:
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message(embed=discord.Embed(
                title="▶️ Music Resumed!",
                description="I’m back! The song is playing again! 🎶",
                color=discord.Color.green()
            ))
        else:
            await interaction.response.send_message("😞 No song is currently paused to resume. 😞", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"💥 Something went wrong while resuming the song: {str(e)} 💥", ephemeral=True)

@bot.tree.command(name="queue", description="Shows the current song queue.")
async def queue_list(interaction: discord.Interaction):
    try:
        if queue:
            queue_str = "\n".join([f"{i+1}. {song_name}" for i, (song_name, _) in enumerate(queue)])
            await interaction.response.send_message(embed=discord.Embed(
                title="📋 Current Queue",
                description=f"Here’s the current song queue:\n{queue_str}",
                color=discord.Color.blue()
            ))
        else:
            await interaction.response.send_message(embed=discord.Embed(
                title="Queue is Empty",
                description="The queue is currently empty! Add some songs to it! 🎶",
                color=discord.Color.red()
            ))
    except Exception as e:
        await interaction.response.send_message(f"💥 Something went wrong while checking the queue: {str(e)} 💥", ephemeral=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()
    print("Slash commands synced!")

bot.run(token)

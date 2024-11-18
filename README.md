# Discord Music Bot

A music-playing bot for Discord that can join voice channels, play songs from YouTube, and manage a queue of tracks. This bot allows users to play, skip, pause, resume, and stop music, along with managing the song queue directly from Discord commands.

## Features

- **Join Voice Channel**: The bot can join your voice channel.
- **Play Songs**: Play songs from YouTube by searching for song names.
- **Queue Management**: Add songs to a queue, skip songs, and view the queue.
- **Pause/Resume Music**: Pause the current song and resume it later.
- **Stop Music**: Stop the music and disconnect the bot from the voice channel.
- **Reconnection Logic**: Handles reconnection automatically if the bot disconnects from the voice channel.

## Requirements

Before running the bot, make sure you have the following dependencies installed:

- Python 3.8 or higher
- `pip` (Python package installer)

### Dependencies

You can install the necessary dependencies by running the following command:

```bash
pip install -r requirements.txt
```

Where the `requirements.txt` file should contain the following:

```txt
discord.py==2.4.0
yt-dlp==2024.11.18
python-dotenv==1.0.1
```

1. **discord.py**: The library used for interacting with the Discord API.
2. **yt-dlp**: A fork of youtube-dl used to download and extract audio from YouTube videos.
3. **python-dotenv**: Used to manage environment variables (for securely storing the Discord bot token).

## Setup

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/Shirozy/Discord-Music-Bot/
cd discord-music-bot
```

### 2. Create a `.env` File

Create a `.env` file to store your Discord bot token securely. You can copy the `.env.example` file and rename it to `.env`:

```bash
cp .env.example .env
```

Then, open the `.env` file and paste your **Discord Bot Token** in place of `TOKEN_HERE`:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
```

### 3. Running the Bot

Once you’ve set up the `.env` file and installed dependencies, you can run the bot with:

```bash
python bot.py
```

When the bot starts, it will log into Discord and sync the slash commands (`/commands`) with your server.

## Command List

### `/join`

- **Description**: Makes the bot join your current voice channel.
- **Usage**: `/join`
- **Response**: The bot joins the voice channel or tells you to join a channel first if you're not in one.

### `/play <song_name>`

- **Description**: Plays a song from YouTube based on the song name provided.
- **Usage**: `/play <song_name>`
- **Example**: `/play Never Gonna Give You Up`
- **Response**: The bot joins the voice channel (if not already joined) and starts playing the song.

### `/stop`

- **Description**: Stops the current song and disconnects the bot from the voice channel.
- **Usage**: `/stop`
- **Response**: The bot will stop playing music and leave the voice channel.

### `/skip`

- **Description**: Skips the current song and plays the next one in the queue.
- **Usage**: `/skip`
- **Response**: The bot will skip to the next song in the queue or announce that the queue is empty.

### `/pause`

- **Description**: Pauses the current song.
- **Usage**: `/pause`
- **Response**: The bot pauses the song if it's currently playing.

### `/resume`

- **Description**: Resumes the paused song.
- **Usage**: `/resume`
- **Response**: The bot will resume playing the song from where it left off.

### `/queue`

- **Description**: Shows the current queue of songs.
- **Usage**: `/queue`
- **Response**: Displays a list of songs in the queue.

## Error Handling

- If the bot is unable to find a song or if any command fails, it will send an error message in the Discord chat.
- If the bot disconnects from a voice channel, it will attempt to reconnect automatically.

## Troubleshooting

- **Bot fails to connect to a voice channel**: Ensure the bot has the correct permissions in your Discord server, including the `Connect` and `Speak` permissions for voice channels.
- **Bot is not playing music**: Ensure you have a valid internet connection and that `yt-dlp` is working correctly by checking for errors in the console logs.
- **No response from the bot**: Make sure the bot is online and that the token in `.env` is correctly set.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to contribute by opening issues or submitting pull requests to improve the functionality of the bot.

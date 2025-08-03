import asyncio
import os
import discord
from discord import FFmpegPCMAudio
from discord.ext import commands
from discord import Intents

TOKEN = os.getenv("DISCORD_TOKEN")

# Define the guilds where the commands will be registered
guilds = [
    discord.Object(id=1401065347859349586),
    discord.Object(id=1281381838375489618),
]

client = commands.Bot(command_prefix="/", intents=Intents.all())

activity_check_task = None
continue_event = None
last_interaction: discord.Interaction = None
restarting_lock = asyncio.Lock()

# 4 hour timer for playing before prompting to continue
PLAY_DURATION = 14400


async def restart_playback():
    """
    Reconnects to the last channel it was connected to (if any) and resumes
    playback.
    """
    global activity_check_task, continue_event, last_interaction

    if restarting_lock.locked():
        print("Restart is already in progress.")
        return

    async with restarting_lock:
        if not last_interaction:
            print("Cannot restart: No last interaction available.")
            return

        voice_channel = last_interaction.user.voice.channel
        if not voice_channel:
            await last_interaction.channel.send(
                "Could not find the previous voice channel to reconnect."
            )
            return

        await last_interaction.channel.send(
            f"An error was detected. Attempting to restart and reconnect to {voice_channel.name}..."
        )

        try:
            if last_interaction.guild.voice_client:
                await last_interaction.guild.voice_client.disconnect()

            await asyncio.sleep(1)

            voice_client = await voice_channel.connect()
            voice_client.play(FFmpegPCMAudio("http://65.108.124.70:7200/stream"))

            if activity_check_task:
                activity_check_task.cancel()

            continue_event = asyncio.Event()
            activity_check_task = client.loop.create_task(
                check_activity(last_interaction)
            )

            await last_interaction.channel.send(
                "Successfully reconnected and restarted playback."
            )
        except Exception as e:
            print(f"Error during restart_playback: {e}")
            await last_interaction.channel.send(
                "Failed to restart playback. Please use the `/play` command manually."
            )
            last_interaction = None


async def check_activity(interaction: discord.Interaction):
    global activity_check_task, continue_event
    try:
        while True:
            if continue_event:
                continue_event.clear()
            await asyncio.sleep(PLAY_DURATION)

            if (
                not interaction.guild.voice_client
                or not interaction.guild.voice_client.is_playing()
            ):
                break

            await interaction.channel.send(
                "Are you still listening? Run the `/continue` command within the next 3 minutes to keep the music going."
            )

            try:
                if continue_event:
                    await asyncio.wait_for(continue_event.wait(), timeout=180.0)
                    await interaction.channel.send("Continuing playback.")
            except asyncio.TimeoutError:
                await interaction.channel.send(
                    "No response received. Stopping playback."
                )
                if interaction.guild.voice_client:
                    interaction.guild.voice_client.stop()
                    await interaction.guild.voice_client.disconnect()
                break
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in check_activity task: {e}")
        await restart_playback()
    finally:
        activity_check_task = None
        continue_event = None


@client.event
async def on_ready():
    print("Connected")

    for guild in guilds:
        await client.tree.sync(guild=guild)


@client.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: discord.app_commands.AppCommandError
):
    print(f"Caught app command error in '{interaction.command.name}': {error}")
    await restart_playback()


@client.tree.command(
    name="play",
    description="Starts playing the underdground bass audio stream.",
    guilds=guilds,
)
async def play(interaction: discord.Interaction):
    global activity_check_task, continue_event, last_interaction

    if not interaction.user.voice:
        await interaction.response.send_message("You are not in a voice channel.")
        return

    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        await interaction.response.send_message(
            f"I'm already streaming underground bass in {interaction.guild.voice_client.channel}. Use `/stop` if you'd like to move me to a different channel."
        )
        return

    voice_channel = interaction.user.voice.channel

    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()

    try:
        await interaction.response.send_message(
            f"Connecting to {voice_channel.name}..."
        )
        voice_client = await voice_channel.connect()
        voice_client.play(FFmpegPCMAudio("http://65.108.124.70:7200/stream"))

        if activity_check_task:
            activity_check_task.cancel()

        continue_event = asyncio.Event()
        activity_check_task = client.loop.create_task(check_activity(interaction))

        # Save context for potential restarts
        last_interaction = interaction

    except Exception as e:
        print(f"Error during initial play command: {e}")
        await restart_playback()


@client.tree.command(
    name="stop", description="Stops the stream and disconnects.", guilds=guilds
)
async def stop(interaction: discord.Interaction):
    global activity_check_task, last_interaction
    if activity_check_task:
        activity_check_task.cancel()
        activity_check_task = None

    if interaction.guild.voice_client:
        interaction.guild.voice_client.stop()
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Playback stopped.")

    # Clear context on intentional stop
    last_interaction = None


@client.tree.command(name="continue", description="Continues playback.", guilds=guilds)
async def continue_(interaction: discord.Interaction):
    """Allows users to signal the bot to continue play back rather than auto-timeout"""
    global continue_event
    if continue_event and not continue_event.is_set():
        continue_event.set()
        await interaction.response.send_message("Continuing playback.")


client.run(TOKEN)

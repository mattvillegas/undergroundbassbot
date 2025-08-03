import asyncio
import os
from discord import FFmpegPCMAudio
from discord.ext import commands
from discord import Intents

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "/"

client = commands.Bot(command_prefix=list(PREFIX), intents=Intents.all())

activity_check_task = None
continue_event = None
last_play_ctx = None
last_voice_channel_id = None
restarting_lock = asyncio.Lock()

# 4 hour timer for playing before prompting to continue
PLAY_DURATION = 14400


async def restart_playback():
    """
    Reconnects to the last channel it was connected to (if any) and resumes
    playback.
    """
    global activity_check_task, continue_event, last_play_ctx, last_voice_channel_id

    if restarting_lock.locked():
        print("Restart is already in progress.")
        return

    async with restarting_lock:
        if not last_play_ctx or not last_voice_channel_id:
            print("Cannot restart: No last play context or channel ID available.")
            return

        ctx = last_play_ctx
        voice_channel = client.get_channel(last_voice_channel_id)

        if not voice_channel:
            await ctx.send("Could not find the previous voice channel to reconnect.")
            return

        await ctx.send(
            f"An error was detected. Attempting to restart and reconnect to {voice_channel.name}..."
        )

        try:
            if ctx.voice_client:
                await ctx.voice_client.disconnect()

            await asyncio.sleep(1)

            voice_client = await voice_channel.connect()
            voice_client.play(FFmpegPCMAudio("http://65.108.124.70:7200/stream"))

            if activity_check_task:
                activity_check_task.cancel()

            continue_event = asyncio.Event()
            activity_check_task = client.loop.create_task(check_activity(ctx))

            await ctx.send("Successfully reconnected and restarted playback.")
        except Exception as e:
            print(f"Error during restart_playback: {e}")
            await ctx.send(
                "Failed to restart playback. Please use the `/play` command manually."
            )
            last_play_ctx = None
            last_voice_channel_id = None


async def check_activity(ctx):
    global activity_check_task, continue_event
    try:
        while True:
            if continue_event:
                continue_event.clear()
            await asyncio.sleep(PLAY_DURATION)

            if not ctx.voice_client or not ctx.voice_client.is_playing():
                break

            await ctx.send(
                "Are you still listening? Run the `/continue` command within the next 3 minutes to keep the music going."
            )

            try:
                if continue_event:
                    await asyncio.wait_for(continue_event.wait(), timeout=180.0)
                    await ctx.send("Continuing playback.")
            except asyncio.TimeoutError:
                await ctx.send("No response received. Stopping playback.")
                if ctx.voice_client:
                    ctx.voice_client.stop()
                    await ctx.voice_client.disconnect()
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


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    print(f"Caught command error in '{ctx.command}': {error}")
    await restart_playback()


@client.command()
async def play(ctx):
    global activity_check_task, continue_event, last_play_ctx, last_voice_channel_id

    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel.")
        return

    voice_channel = ctx.author.voice.channel

    if ctx.voice_client:
        await ctx.voice_client.disconnect()

    try:
        voice_client = await voice_channel.connect()
        voice_client.play(FFmpegPCMAudio("http://65.108.124.70:7200/stream"))

        if activity_check_task:
            activity_check_task.cancel()

        continue_event = asyncio.Event()
        activity_check_task = client.loop.create_task(check_activity(ctx))

        # Save context for potential restarts
        last_play_ctx = ctx
        last_voice_channel_id = voice_channel.id

    except Exception as e:
        print(f"Error during initial play command: {e}")
        await restart_playback()


@client.command(aliases=["s", "sto"])
async def stop(ctx):
    global activity_check_task, last_play_ctx, last_voice_channel_id
    if activity_check_task:
        activity_check_task.cancel()
        activity_check_task = None

    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()

    # Clear context on intentional stop
    last_play_ctx = None
    last_voice_channel_id = None


@client.command(name="continue")
async def continue_(ctx):
    """Signals the bot to continue playing."""
    global continue_event
    if continue_event and not continue_event.is_set():
        continue_event.set()


client.run(TOKEN)

import asyncio
import os
from discord import FFmpegPCMAudio
from discord.ext.commands import Bot
from discord import Intents

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "/"

client = Bot(command_prefix=list(PREFIX), intents=Intents.all())

activity_check_task = None
continue_event = None

# 4 hour timer for playing before prompting to continue
PLAY_DURATION = 14400

async def check_activity(ctx):
    global activity_check_task, continue_event
    try:
        while True:
            if continue_event:
                continue_event.clear()
            await asyncio.sleep(PLAY_DURATION)

            if not ctx.voice_client or not ctx.voice_client.is_playing():
                break

            await ctx.send("Are you still listening? Run the `/continue` command within the next 3 minutes to keep the music going.")

            try:
                # Wait for the continue command to set the event
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
    finally:
        activity_check_task = None
        continue_event = None


@client.event
async def on_ready():
    print("Connected")


@client.command()
async def play(ctx):
    global activity_check_task, continue_event

    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel.")
        return

    voice_channel = ctx.author.voice.channel

    if ctx.voice_client:
        await ctx.voice_client.disconnect()

    try:
        voice_client = await voice_channel.connect()
        voice_client.play(FFmpegPCMAudio('http://65.108.124.70:7200/stream'))

        if activity_check_task:
            activity_check_task.cancel()

        continue_event = asyncio.Event()
        activity_check_task = client.loop.create_task(check_activity(ctx))

    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("An error occurred while trying to connect to the voice channel.")


@client.command(aliases=['s', 'sto'])
async def stop(ctx):
    global activity_check_task
    if activity_check_task:
        activity_check_task.cancel()
        activity_check_task = None

    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()


@client.command(name='continue')
async def continue_(ctx):
    """Signals the bot to continue playing."""
    global continue_event
    if continue_event and not continue_event.is_set():
        continue_event.set()
    else:
        await ctx.send("The bot is not waiting for a continuation, or it has already been continued.")


client.run(TOKEN)

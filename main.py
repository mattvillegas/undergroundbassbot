import os
from discord import FFmpegPCMAudio, FFmpegOpusAudio
from discord.ext.commands import Bot
from discord import utils
from discord import VoiceChannel, VoiceClient
from discord import Intents

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "/"

client = Bot(command_prefix=list(PREFIX), intents=Intents.all())


@client.event
async def on_ready():
    print("Connected")


@client.command(guild="1281381838375489618")
async def play(ctx, url: str = 'http://65.108.124.70:7200/stream'):
    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel.")
        return

    voice_channel = ctx.author.voice.channel

    if ctx.voice_client:
        await ctx.voice_client.disconnect()

    try:
        voice_client = await voice_channel.connect()
        voice_client.play(FFmpegPCMAudio(url))
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("An error occurred while trying to connect to the voice channel.")


@client.command(guild="1281381838375489618",aliases=['s', 'sto'])
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()

client.run(TOKEN)

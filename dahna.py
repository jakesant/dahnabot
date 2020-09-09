#A Discord bot written in Python
#https://realpython.com/how-to-make-a-discord-bot-python/
#https://youtu.be/nW8c7vT6Hl4

import asyncio
import discord
import youtube_dl
from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}
client = commands.Bot(command_prefix = '$')

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('With yo mamma'))
    print('Dahna.')

@client.event
async def on_member_join(member):
    print(f'{member} has joined the server!')

@client.command()
async def hello(ctx):
    #await ctx.send(f'Hello {ctx.author.name}!')
    await ctx.send(F"F'ghoxx il-liba ommok {ctx.author.name}!")

@client.command()
async def join(ctx):
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(ctx.author.voice.channel)

    await ctx.author.voice.channel.connect()

@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()

@client.command()
async def ping(ctx):
    await ctx.send(f'{ctx.author.name} ping is {round(client.latency * 1000)}ms')

@client.command()
async def play(ctx, *, url):

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=None)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('Now playing: {}'.format(player.title))


client.run('token')
#Discord Bot made by Kevin Lin
#Plays some funny sound effects, plays Youtube URLS or the top Youtube search query for a string
#Contains a lot of inside jokes, but also a lot of good Discord.py functionality
#Just a personal project run on Pycharm
#Last edited 9/2/2020


import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
import re
import requests
import asyncio
import json

#Get Discord Token from gitignored config.json
with open('config.json') as config_file:
    config = json.load(config_file)

#Discord.py API Code
TOKEN = config['keys']['token']
client = commands.Bot(command_prefix='!ob ')

#Global variable for remembering the last played song
lastplayedname = 'No songs have been played yet'

#Checks every message
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    #I wanted OmenBot to accept any length of hmmmmm but this doesn't seem to work
    if re.match(r'!ob h.m+\*', message.content):
        await message.channel.send(message.content[3:])
    #George frequently does not do his homework so this is just a fun auto message
    if 'GEORGE' in message.content.upper():
        msg = 'George go do your homework'.format(message)
        await message.channel.send(msg)
    await client.process_commands(message)

#Logs in at the start
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)

#Joins your voice channel if its not already, plays the Omen (Valorant) sound effect hmm. Pass -l to leave after
@client.command(aliases=['hm', 'hmmm', 'hmmmm', 'hmmmmm', 'hmmmmmm', 'hmmmmmmm'], brief='hmm', description='options: -l to leave after,-t to tts')
async def hmm(ctx, arg1 ='dog'):
    await join(ctx)
    voice = get(client.voice_clients, guild=ctx.guild)
    voice.play(discord.FFmpegPCMAudio("sounds/hmm.mp3"), after=lambda e: print(ctx.message.content[3:]))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.37
    if(arg1 == '-t'):
        await ctx.send("hmm", tts=True)
    else:
        await ctx.send(ctx.message.content[3:])
    await asyncio.sleep(3)
    if(arg1 == '-l'):
        await leave(ctx)

#Prints bald and then sends text to speech bald
@client.command(brief='bald', description='Types bald twice, once with text to speech')
async def bald(ctx, arg1 ='dog'):
    await ctx.send("bald")
    await ctx.send("bald", tts=True)

#Sends text to speech with *arg to accept multiple arguments
@client.command(brief='Text to speech for whatever text you pass it', description='Pass speech as an argument after and OmenBot will say it')
async def tts(ctx, *arg1):
    arg1 = " ".join(arg1[:])
    await ctx.send(arg1, tts=True)

#Same as hmm but with Za Warudo
@client.command(aliases=['zawarudo', 'za warudo', 'za_warudo', 'warudo'],brief = 'plays Za Warudo sound effect, -l to leave after')
async def za(ctx, arg1='dog'):
    await join(ctx)
    voice = get(client.voice_clients, guild=ctx.guild)
    voice.play(discord.FFmpegPCMAudio("sounds/ZAWARUDO.mp3"), after=lambda e: print(ctx.message.content[3:]))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.85
    await ctx.send(ctx.message.content[3:])
    await asyncio.sleep(5)
    if (arg1 == '-l'):
        await leave(ctx)

#Same as hmm but with kekw. Also accepts -l for leaving, with arg2 being
@client.command(aliases=['kek', 'lulw', 'k'], brief='KEKW')
async def kekw(ctx, *arg1):
    arg1 = " ".join(arg1[:])
    await join(ctx)
    voice = get(client.voice_clients, guild=ctx.guild)
    if '-long' in arg1:
        voice.play(discord.FFmpegPCMAudio("sounds/KEKWLONG.mp3"), after=lambda e: print(ctx.message.content[3:]))
    else:
        voice.play(discord.FFmpegPCMAudio("sounds/KEKW.mp3"), after=lambda e: print(ctx.message.content[3:]))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.85
    await ctx.send(ctx.message.content[3:])
    await asyncio.sleep(5)
    if ('-l' in arg1):
        await leave(ctx)

#Joins the voice channel that you're in
@client.command(aliases=['j', 'joi'], brief='Joins the voice channel that you\'re in')
async def join(ctx):
    global voice
    channel = ctx.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send(f"Joined {channel}")

#Leaves the voice channel that you're in
@client.command(aliases=['l'],brief='Leaves the voice channel')
async def leave(ctx):
    channel = ctx.guild.voice_client.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}")
        await ctx.send(f"Left {channel}")
    else:
        print("Bot was told to leave voice channel, but was not in one\n")
        await ctx.send("I don't think I'm in a voice channel")

#Uses Notify API to tell you how many people are in space
@client.command(brief='Self-explanatory')
async def howmanypeopleinspacern(ctx):
    people = requests.get('http://api.open-notify.org/astros.json')
    people_json = people.json()['number']
    names_json = people.json()['people']
    await ctx.send(f'Number of people in space: {people_json}: {names_json}')

#Uses Open Notify API to tell you where the iss is
@client.command(brief='Self-explanatory')
async def whereistheiss(ctx):
    request = requests.get("http://api.open-notify.org/iss-now.json")
    latitude = request.json()['iss_position']['latitude']
    longitude = request.json()['iss_position']['longitude']
    await ctx.send(f'The ISS is at: {latitude}, {longitude}')

#Takes a Youtube url or a youtube search query and then plays it
@client.command(aliases=['p'], brief='Plays a Youtube link or YT search query if its <10 m')
async def play(ctx, *url: str):
    await join(ctx)
    #takes multiple words as argument for longer search queries
    url = " ".join(url[:])
    text = False
    #checks for existing song.mp3 and deletes if so
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file\n")
    except PermissionError: #Can't play two songs at once
        print("Trying to delete song file, but it's being played\n")
        await ctx.send("Error: Music playing")
        return
    #if trying to play a playlist, deny
    if "?list" in url:
        await ctx.send("No playlists please!")
        return
    #if it's a normal link, proceed
    elif "https" in url:
        await ctx.send("Fetching from Youtube...")
    #if it's a search query, make slight changes
    else:
        await ctx.send(f"Searching Youtube for {url}")
        text = True

    voice = get(client.voice_clients, guild=ctx.guild)
    #use youtube_dl to get the video from url or query
    ydl_opts = {
        'default_search': 'auto',
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        dict = ydl.extract_info(
            url,
            download=False)
        print(dict)
        if text: #if the request was a text search instead of a url, the extract_info dict will be different
            if len(dict['entries']) == 0:
                await ctx.send("No results found")
                return
            if dict['entries'][0]['duration'] > 10 * 60: #If the video is too long
                await ctx.send("Video longer than 10 minutes, stop trying to kill Kevin's C drive :(")
                return
            else:
                ydl.download([url])
        else:
            if dict['duration'] > 10 * 60:#if the video is too long, don't download
                await ctx.send("Video longer than 10 minutes, stop trying to kill Kevin's C drive :(")
                return
            else:
                ydl.download([url])
    #find the newly downloaded video and rename it. Save other sound effects in sounds so there's no conflicts
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            global lastplayedname
            lastplayedname = name
            print("Renaming")
            os.rename(file, "song.mp3")
    #play the song
    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print(f"{name} has finished playing"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    #volume that seemed to work
    voice.source.volume = 0.50
    nname = name.rsplit("-", 2)
    await ctx.send(f"Playing: {nname}")
    print("playing\n")

#Repeats the last song played
@client.command(aliases=['replay','restart'], brief='Repeats the last video from play')
async def repeat(ctx):
    name = lastplayedname
    if(name == 'No songs have been played yet'):
        await ctx.send(name)
        return

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print(f"{name} has finished playing"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.50
    nname = lastplayedname.rsplit("-", 2)
    await ctx.send(f"Playing: {nname}")
    print("playing\n")

#Pauses current song
@client.command(aliases=['pa'], brief='Pauses the music currently being played')
async def pause(ctx):
    voice = get(client.voice_clients, guild = ctx.guild)
    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Music paused, use \"!ob resume\" to resume")
    else:
        print("Music not playing")
        await ctx.send("There is no music playing, failed to pause")

@client.command(aliases=['re'], brief='Resumes paused music')
async def resume(ctx):
    voice = get(client.voice_clients, guild = ctx.guild)
    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("Resumed music")
    else:
        print("Music is not paused")
        await ctx.send("Music is not paused")

@client.command(aliases=['st'], brief='Stops music')
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("Music stopped")
    else:
        print("Music not playing")
        await ctx.send("There is no music playing, failed to stop")
#Runs the bot
client.run(TOKEN)

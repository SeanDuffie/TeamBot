""" @file discord_bot.py
    @author Sean Duffie
    @brief Discord bot interface

    The Team Bot is designed to help servers that host competitive lobbies where a group will
    split into two teams and play against each other. It will provide several different options
    for splitting up a team, including polls for self selection, team captains, or randomly
    assigning all members. There will also be options for having different amounts of teams, or
    having a spectator.

    Resources:
        - https://discordpy.readthedocs.io/en/latest/api.html
"""
import datetime
import os
import random
from typing import List

import discord
import discord.ext
import discord.ext.commands
import discord.ext.tasks
import dotenv

# Set Discord intents (these are permissions that determine what the bot is allowed to observe)
intents = discord.Intents.default()
# intents.members = True
# intents.message_content = True

############### SET TIME HERE ###############
LOCAL_TZ = datetime.datetime.now().astimezone().tzinfo
#############################################

############ GET ENVIRONMENT VARIABLES ############
RTDIR = os.path.dirname(__file__)

dotenv.load_dotenv(dotenv_path=f"{RTDIR}/.env")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
###################################################

# NOTE: I use commands.Bot because it extends features of the Client to allow things like commands
# Initialize Discord Bot
discord_bot = discord.ext.commands.Bot(
    command_prefix="/",
    intents=intents,
    help_command=discord.ext.commands.HelpCommand()
)

@discord_bot.event
async def on_ready():
    """ Plays when the bot is installed (When running or installed?) """
    # Set the Bot Rich Presence
    await discord_bot.change_presence(
        activity=discord.Game(name="Today's Wordle")
    )

async def splitTeams(self, message: discord.Message):
    command = message.content.split()
    maxteamsize = 0
    if len(command) > 1:
        try:
            maxteamsize = int(command[1])
        except:
            await message.channel.send('Hey {0.author.mention}, the max team size has to be a positive integer (no decimals!) not "{1}" - Be Better!'.format(message, channel[1]))
            return
    if maxteamsize < 0:
        await message.channel.send('Hey {0.author.mention}, the max team size has to be a postive integer (no decimals!) not "{1}" - Be Better!'.format(message, channel[1]))
        return
    channels = await self.GetChannelList(message)
    lobby = await self.GetLobbyChannel(channels)
    members = lobby.members
    # get member count
    numplayers = len(members)
    if numplayers == 0:
        await message.channel.send('Hey, no one is in the lobby!  Get in the lobby and then ask me to split the teams')
        return
    if maxteamsize == 0:
        maxteamsize = math.ceil(numplayers/2)
    # get number of teams
    numteams = math.ceil(numplayers/maxteamsize)
    # get channels they are being shifted to
    MoveToChannels = await self.GetChannels(channels, numteams)
    # shuffle members
    random.shuffle(members)
    teamNumber = 0
    # move members
    for member in members:
        await member.move_to(MoveToChannels[teamNumber])
        teamNumber += 1
        if teamNumber == numteams:
            teamNumber = 0
    await message.channel.send('Ready set go! Have fun!')

async def GetChannels(self, channels: List[discord.VoiceChannel], numchannels: int):
    # shuffle channels to make it random
    gotochannels = []
    random.shuffle(channels)
    for c in channels:
        # if the destination channel is empty and not the Lobby
        if len(c.members) == 0 and c.name != 'Lobby' :
            gotochannels.append(c)
            if len(gotochannels) == numchannels:
                return gotochannels

async def GetChannelList(self, message: discord.Message):
    channels = message.guild.voice_channels
    return channels

async def GetLobbyChannel(self, channels: List[discord.VoiceChannel]):
     for c in channels:
         if c.name == 'Lobby':
             return c

@discord_bot.command
async def command(ctx: discord.ext.commands.context.Context, arg1: str = None):
    """ Command that takes a singe parameter """
    await ctx.send(f"Entered command! Arg 1: {arg1}")

discord_bot.run(DISCORD_TOKEN)

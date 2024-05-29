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
import math
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

@discord_bot.command
async def shuffle(ctx: discord.ext.commands.context.Context, mode: str = "1", teams: int = 2):
    """_summary_

    Args:
        ctx (discord.ext.commands.context.Context): _description_
        mode (str, optional): _description_. Defaults to "1".
        teams (int, optional): _description_. Defaults to 2.
    """
    print(mode)
    maxteamsize = 0
    try:
        maxteamsize = int(teams)
    except Exception as e:
        print(e)
        await ctx.send(
            f'Hey {ctx.author.mention}, the max team size has to be an integer (no decimals!), not "{teams}" - Be Better!'
        )
        return
    if maxteamsize < 0:
        await ctx.send(
            f'Hey {ctx.author.mention},the max team size has to be postive, not "{teams}" - Be Better!'
        )
        return
    channels = await get_channel_list(ctx)
    lobby = await get_lobby_channel(channels)
    members = lobby.members
    # get member count
    numplayers = len(members)
    if numplayers == 0:
        await ctx.send('Hey, no one is in the lobby!  Get in the lobby and then ask me to split the teams')
        return
    if maxteamsize == 0:
        maxteamsize = math.ceil(numplayers/2)
    # get number of teams
    numteams = math.ceil(numplayers/maxteamsize)
    # get channels they are being shifted to
    move_channels = await get_channels(channels, numteams)
    # shuffle members
    random.shuffle(members)
    team_number = 0
    # move members
    for member in members:
        await member.move_to(move_channels[team_number])
        team_number += 1
        if team_number == numteams:
            team_number = 0
    await ctx.send('Ready set go! Have fun!')

async def get_channels(channels: List[discord.VoiceChannel], numchannels: int):
    """_summary_

    Args:
        channels (List[discord.VoiceChannel]): _description_
        numchannels (int): _description_

    Returns:
        _type_: _description_
    """
    # shuffle channels to make it random
    gotochannels = []
    random.shuffle(channels)
    for c in channels:
        # if the destination channel is empty and not the Lobby
        if len(c.members) == 0 and c.name != 'Lobby' :
            gotochannels.append(c)
            if len(gotochannels) == numchannels:
                return gotochannels

async def get_channel_list(ctx: discord.ext.commands.context.Context):
    """_summary_

    Args:
        ctx (discord.ext.commands.context.Context): _description_

    Returns:
        _type_: _description_
    """
    channels = ctx.guild.voice_channels
    return channels

async def get_lobby_channel(channels: List[discord.VoiceChannel]):
    """_summary_

    Args:
        channels (List[discord.VoiceChannel]): _description_

    Returns:
        _type_: _description_
    """
    for c in channels:
        if c.name == 'Lobby':
            return c

discord_bot.run(DISCORD_TOKEN)

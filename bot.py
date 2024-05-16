""" @file discord_bot.py
    @author Sean Duffie
    @brief Discord bot interface

    This is a template file for discord bots that will be used in the future to jumpstart the
    development process for new bots.

    Resources:
        - https://discordpy.readthedocs.io/en/latest/api.html
"""
import datetime
import os

import discord
import discord.ext
import discord.ext.commands
import discord.ext.tasks
import dotenv

# Set Discord intents (these are permissions that determine what the bot is allowed to observe)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

############### SET TIME HERE ###############
LOCAL_TZ = datetime.datetime.now().astimezone().tzinfo
TIMES = [
    datetime.time(6, tzinfo=LOCAL_TZ),
    datetime.time(12, tzinfo=LOCAL_TZ),
    datetime.time(18, tzinfo=LOCAL_TZ),
    datetime.time(0, tzinfo=LOCAL_TZ)
]
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
    # Start the scheduled task
    if not tasks.is_running():
        tasks.start()

    # Set the Bot Rich Presence
    await discord_bot.change_presence(
        activity=discord.Game(name="Today's Wordle")
    )

# @discord_bot.event
# async def on_message(msg: discord.message.Message):
#     # Bot shouldn't be responding to itself
#     if msg.author == discord_bot.user:
#         return
#     if msg.content.lower() == "hello":
#         await msg.channel.send(content="World")
#     if "sleep" in msg.content.lower():
#         await discord_bot.change_presence(
#             status=discord.Status.do_not_disturb,
#             activity=discord.Game(name="Sleeping...😴")
#         )

@discord_bot.command
async def command(ctx: discord.ext.commands.context.Context, arg1: str = None):
    """ Command that takes a singe parameter """
    await ctx.send(f"Entered command! Arg 1: {arg1}")

@discord.ext.tasks.loop(time=TIMES)
async def tasks():
    """ Repeating task that plays every 6 hours """
    print(f"Time: {datetime.datetime.now()}")

discord_bot.run(DISCORD_TOKEN)

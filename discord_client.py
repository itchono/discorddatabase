import discord
from discord.ext import commands

intents = discord.Intents(guilds=True, messages=True)

client = commands.Bot(
    command_prefix="$w ",
    case_insensitive=True,
    status=discord.Status.online,
    activity=discord.Game("[$w ] W for Wombo"),
    intents=intents)

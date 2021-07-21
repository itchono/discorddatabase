import discord
from discord.ext import commands
from discord_slash import SlashCommand

intents = discord.Intents(guilds=True, messages=True)

client = commands.Bot(
    command_prefix="$w ",
    case_insensitive=True,
    status=discord.Status.online,
    activity=discord.Game("W for Wombo"),
    intents=intents)

slash = SlashCommand(client, delete_from_unused_guilds=True)

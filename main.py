import dotenv
import os
from database import Database
from bot_commands import DatabaseCmds

from discord_client import client as bot
from discord import HTTPException

dotenv.load_dotenv()  # Load .env file, prior to components loading

wdb = Database(bot)

bot.add_cog(DatabaseCmds(bot, wdb))


@bot.event
async def on_ready():
    print(
        f"{bot.user} is online, logged into {len(bot.guilds)} server(s).")
    await wdb.startup(int(os.environ.get("GUILD")))

try:
    bot.run(os.environ.get("TOKEN"))  # Run bot with loaded password
except HTTPException:
    os.system("kill 1")  # hard restart on 429

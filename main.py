import dotenv
import os
from database import Database
from bot_commands import DatabaseCmds

from discord_client import client as bot
from web_interface import app
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
    bot.loop.create_task(app.run_task(host="0.0.0.0", port=8080))
    bot.run(os.environ.get("TOKEN"))
except HTTPException:
    os.system("kill 1")  # hard restart on 429

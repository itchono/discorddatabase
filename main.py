import dotenv
import os
from database import Database

from discord_client import client as bot
from discord import HTTPException

dotenv.load_dotenv()  # Load .env file, prior to components loading

bot.add_cog(Database(bot))


@bot.event
async def on_ready():
    print(
        f"{bot.user} is online, logged into {len(bot.guilds)} server(s).")

try:
    bot.run(os.environ.get("TOKEN"))  # Run bot with loaded password
except HTTPException:
    os.system("kill 1")  # hard restart on 429

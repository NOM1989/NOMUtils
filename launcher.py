from dotenv import load_dotenv

load_dotenv()

from os import getenv
from bot import NOMUtils
import asyncpg
import asyncio
import logging
import discord


async def run_bot():
    try:
        if not debug_mode:
            credentials = {
                "user": getenv("DB_USERNAME"),
                "password": getenv("DB_PASS"),
                "database": getenv("DB_NAME"),
                "host": getenv("DB_HOST"),
            }
            pool = await asyncpg.create_pool(**credentials)
    except Exception:
        print("Could not connect to DB")
        return

    async with NOMUtils() as bot:
        if not debug_mode:
            bot.pool = pool
        await bot.start(getenv("BOT_TOKEN"))


debug_mode = True  # whether or not to connect to the db (True means dont connect)
if __name__ == "__main__":
    discord.utils.setup_logging(level=logging.INFO, root=False)
    asyncio.run(run_bot())

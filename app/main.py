import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

import sys

sys.path.append("/app")

from app.database import init_db
from app.handlers import register_handlers
from app.middlewares import DatabaseMiddleware

logging.basicConfig(level=logging.INFO)


async def main():
    load_dotenv()

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    register_handlers(dp)

    SessionLocal = await init_db(DATABASE_URL)

    dp.update.outer_middleware.register(DatabaseMiddleware(SessionLocal))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

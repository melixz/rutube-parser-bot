import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from app.database import init_db
from app.handlers import register_handlers

logging.basicConfig(level=logging.INFO)


async def main():
    load_dotenv()

    BOT_TOKEN = os.getenv("BOT_TOKEN")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    register_handlers(dp)

    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

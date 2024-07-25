import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from app.middlewares import DatabaseMiddleware
from app.handlers import register_handlers
from app.db.session import SessionLocal
from app.config import config  # Импортируем config
from aiogram.client.default import (
    DefaultBotProperties,
)  # Импортируем DefaultBotProperties


async def main():
    logging.basicConfig(level=logging.INFO)

    if config.BOT_TOKEN is None:
        raise ValueError("No BOT_TOKEN provided")

    session = AiohttpSession()
    bot = Bot(
        token=config.BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация middleware для сессий базы данных
    dp.update.outer_middleware(DatabaseMiddleware(SessionLocal))

    register_handlers(dp)

    await bot.set_my_commands(
        [
            BotCommand(command="/start", description="Запуск бота"),
            BotCommand(command="/parse", description="Парсинг видео"),
            BotCommand(command="/list", description="Список видео"),
        ]
    )

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from app.middlewares import DatabaseMiddleware
from app.db.session import SessionLocal
from app.config import config
from app.handlers.start import start_router
from app.handlers.parse import parse_router
from app.handlers.list import list_router
from app.handlers.video import video_router


async def main():
    logging.basicConfig(level=logging.INFO)
    session = AiohttpSession()
    bot = Bot(
        token=config.BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(DatabaseMiddleware(SessionLocal))
    dp.callback_query.middleware(DatabaseMiddleware(SessionLocal))

    dp.include_router(start_router)
    dp.include_router(parse_router)
    dp.include_router(list_router)
    dp.include_router(video_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from app.middlewares import DatabaseMiddleware
from app.handlers.start import start_handler
from app.handlers.parse import parse_start, parse_channel_url, parse_video_count
from app.handlers.list import list_start, list_channel_name
from app.handlers.video import (
    video_details_handler,
    handle_all_messages,
    channel_selection_handler,
)
from app.db.session import SessionLocal
from app.config import config
from aiogram.filters import Command
from handlers.states import ParseStates, ListStates


def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command(commands=["start"]))
    dp.message.register(parse_start, Command(commands=["parse"]))
    dp.message.register(list_start, Command(commands=["list"]))
    dp.message.register(parse_channel_url, ParseStates.waiting_for_channel_url)
    dp.message.register(parse_video_count, ParseStates.waiting_for_video_count)
    dp.message.register(list_channel_name, ListStates.waiting_for_channel_name)
    dp.callback_query.register(
        video_details_handler, lambda c: c.data.startswith("details_")
    )
    dp.callback_query.register(
        channel_selection_handler, lambda c: c.data.startswith("channel_")
    )
    dp.message.register(handle_all_messages)


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

    register_handlers(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

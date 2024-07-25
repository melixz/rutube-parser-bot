import logging
from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from app.services.parsing_service import ParserService
from app.services.db_saving_service import SavingService
from app.repositories.video_repository import VideoRepository
from app.keyboards import get_video_keyboard
from sqlalchemy.ext.asyncio import AsyncSession

video_repo = VideoRepository()
saving_service = SavingService(video_repo)


async def start_handler(message: types.Message):
    await message.reply(
        "Привет! Вставьте ссылку на канал RUTUBE и укажите количество видео для парсинга."
    )


async def parse_handler(message: types.Message, db: AsyncSession):
    try:
        logging.info(f"Получено сообщение: {message.text}")
        parts = message.text.split()
        if len(parts) != 3:
            raise ValueError("Неверный формат команды")
        _, channel_url, video_count = parts
        video_count = int(video_count)
        logging.info(f"Парсинг канала: {channel_url} для {video_count} видео")

        videos = await ParserService.parse_channel(channel_url, video_count)
        await saving_service.save_videos(db, videos)

        for video in videos:
            await message.reply(
                f"Сохранено видео: {video['title']}",
                reply_markup=get_video_keyboard(video["video_url"]),
            )

        await message.reply("Видео успешно сохранены!")
    except ValueError as ve:
        logging.error(f"Ошибка: {ve}")
        await message.reply(f"Ошибка: {ve}")
    except Exception as e:
        logging.error(f"Ошибка при обработке команды: {e}")
        await message.reply(
            "Ошибка при обработке команды. Проверьте правильность ввода."
        )


async def list_videos_handler(message: types.Message, db: AsyncSession):
    try:
        logging.info(f"Получено сообщение: {message.text}")
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError("Неверный формат команды")
        _, channel_name = parts
        logging.info(f"Получение списка видео для канала: {channel_name}")

        videos = await video_repo.get_videos_by_channel(db, channel_name)
        if videos:
            for video in videos:
                await message.reply(
                    f"Название: {video.title}\nОписание: {video.description}\nПросмотры: {video.views}\nСсылка: {video.video_url}"
                )
        else:
            await message.reply("Видео не найдены для указанного канала.")
    except ValueError as ve:
        logging.error(f"Ошибка: {ve}")
        await message.reply(f"Ошибка: {ve}")
    except Exception as e:
        logging.error(f"Ошибка при обработке команды: {e}")
        await message.reply(
            "Ошибка при обработке команды. Проверьте правильность ввода."
        )


async def video_details_handler(callback_query: CallbackQuery, db: AsyncSession):
    video_id = callback_query.data.split("_")[1]
    video = await video_repo.get_video_by_id(db, video_id)
    if video:
        await callback_query.message.reply(
            f"Название: {video.title}\nОписание: {video.description}\nПросмотры: {video.views}\nСсылка: {video.video_url}"
        )
    else:
        await callback_query.message.reply("Видео не найдено.")


def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command(commands=["start"]))
    dp.message.register(parse_handler, Command(commands=["parse"]))
    dp.message.register(list_videos_handler, Command(commands=["list"]))
    dp.callback_query.register(
        video_details_handler, lambda c: c.data.startswith("details_")
    )

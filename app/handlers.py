import logging
from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from app.services.parsing_service import ParsingService
from app.database import get_db
from app.repository import VideoRepository
from app.keyboards import get_video_keyboard


async def start_handler(message: types.Message):
    await message.reply(
        "Привет! Вставьте ссылку на канал RUTUBE и укажите количество видео для парсинга."
    )


async def parse_handler(message: types.Message):
    try:
        logging.info(f"Получено сообщение: {message.text}")
        _, channel_url, video_count = message.text.split()
        video_count = int(video_count)
        logging.info(f"Парсинг канала: {channel_url} для {video_count} видео")

        videos = await ParsingService.fetch_videos(channel_url, video_count)
        async for db in get_db():
            for video in videos:
                video["channel_id"] = channel_url
                saved_video = await VideoRepository.add_video(db, video)
                await message.reply(
                    f"Сохранено видео: {saved_video.title}",
                    reply_markup=get_video_keyboard(saved_video.id),
                )

        await message.reply("Видео успешно сохранены!")
    except ValueError:
        logging.error("Количество видео должно быть числом.")
        await message.reply("Ошибка: Количество видео должно быть числом.")
    except Exception as e:
        logging.error(f"Ошибка при обработке команды: {e}")
        await message.reply(
            "Ошибка при обработке команды. Проверьте правильность ввода."
        )


async def list_videos_handler(message: types.Message):
    try:
        logging.info(f"Получено сообщение: {message.text}")
        _, channel_url = message.text.split()
        logging.info(f"Получение списка видео для канала: {channel_url}")

        async for db in get_db():
            videos = await VideoRepository.get_videos_by_channel(db, channel_url)
            if videos:
                for video in videos:
                    await message.reply(
                        f"Название: {video.title}\nОписание: {video.description}\nПросмотры: {video.views}\nСсылка: {video.url}"
                    )
            else:
                await message.reply("Видео не найдены для указанного канала.")
    except Exception as e:
        logging.error(f"Ошибка при обработке команды: {e}")
        await message.reply(
            "Ошибка при обработке команды. Проверьте правильность ввода."
        )


async def video_details_handler(callback_query: CallbackQuery):
    video_id = callback_query.data.split("_")[1]
    async for db in get_db():
        video = await VideoRepository.get_video_by_id(db, video_id)
        if video:
            await callback_query.message.reply(
                f"Название: {video.title}\nОписание: {video.description}\nПросмотры: {video.views}\nСсылка: {video.url}"
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

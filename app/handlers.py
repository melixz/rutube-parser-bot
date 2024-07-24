import logging
from aiogram import Dispatcher, types
from aiogram.filters import Command
from app.services.parsing_service import ParserService
from app.repositories.video_repository import VideoRepository
from app.db.session import get_db
from app.db.models.video import Video
from app.keyboards import get_video_keyboard

video_repo = VideoRepository()


async def start_handler(message: types.Message):
    await message.reply(
        "Привет! Вставьте ссылку на канал RUTUBE и укажите количество видео для парсинга."
    )


async def parse_handler(message: types.Message):
    try:
        logging.info(f"Получено сообщение: {message.text}")
        parts = message.text.split()
        if len(parts) != 3:
            raise ValueError("Неверный формат команды")
        _, channel_url, video_count = parts
        video_count = int(video_count)
        logging.info(f"Парсинг канала: {channel_url} для {video_count} видео")

        videos = await ParserService.parse_channel(channel_url, video_count)
        async for db in get_db():
            for video_data in videos:
                video = Video(
                    title=video_data["title"],
                    description=video_data["description"],
                    views=video_data["views"],
                    video_url=video_data["video_url"],
                    channel_name=video_data["channel_name"],
                )
                saved_video = await video_repo.add_video(video)
                await message.reply(
                    f"Сохранено видео: {saved_video.title}",
                    reply_markup=get_video_keyboard(saved_video.id),
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


async def list_videos_handler(message: types.Message):
    try:
        logging.info(f"Получено сообщение: {message.text}")
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError("Неверный формат команды")
        _, channel_name = parts
        logging.info(f"Получение списка видео для канала: {channel_name}")

        async for db in get_db():
            videos = await video_repo.get_videos_by_channel(channel_name)
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


def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command(commands=["start"]))
    dp.message.register(parse_handler, Command(commands=["parse"]))
    dp.message.register(list_videos_handler, Command(commands=["list"]))

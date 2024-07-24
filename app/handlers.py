import logging
from aiogram import Dispatcher, types
from aiogram.filters import Command
from app.services.parsing_service import ParsingService
from app.services.saving_service import SavingService
from app.database import get_db


async def start_handler(message: types.Message):
    await message.reply("Привет! Вставьте ссылку на канал RUTUBE и укажите количество видео для парсинга.")


async def parse_handler(message: types.Message):
    try:
        logging.info(f"Получено сообщение: {message.text}")
        _, channel_url, video_count = message.text.split()
        video_count = int(video_count)
        logging.info(f"Парсинг канала: {channel_url} для {video_count} видео")

        videos = await ParsingService.fetch_videos(channel_url, video_count)
        async for db in get_db():
            await SavingService.save_videos(videos, db)

        await message.reply("Видео успешно сохранены!")
    except ValueError:
        logging.error("Количество видео должно быть числом.")
        await message.reply("Ошибка: Количество видео должно быть числом.")
    except Exception as e:
        logging.error(f"Ошибка при обработке команды: {e}")
        await message.reply("Ошибка при обработке команды. Проверьте правильность ввода.")


def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command(commands=['start']))
    dp.message.register(parse_handler, Command(commands=['parse']))

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


def escape_markdown(text: str) -> str:
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)


async def start_handler(message: types.Message):
    await message.reply(
        "Привет! Вставьте ссылку на канал RUTUBE и укажите количество видео для парсинга.\n"
        "Примеры команд:\n"
        "/parse https://rutube.ru/metainfo/tv/405933/ 5\n"
        "/list Титаны\n"
        "/video https://rutube.ru/video/f017614595b8c57d5be29dc174bffe9a/"
    )


async def parse_handler(message: types.Message, db: AsyncSession):
    try:
        logging.info(f"Получено сообщение: {message.text}")
        parts = message.text.split()
        if len(parts) != 3:
            raise ValueError(
                "Неверный формат команды. Используйте: /parse <URL канала> <количество видео>"
            )
        _, channel_url, video_count = parts
        video_count = int(video_count)
        logging.info(f"Парсинг канала: {channel_url} для {video_count} видео")

        if not channel_url.startswith(("http://", "https://")):
            channel_url = "http://" + channel_url

        videos = await ParserService.parse_channel(channel_url, video_count)
        await saving_service.save_videos(db, videos)

        for video in videos:
            await message.reply(
                f"Сохранено видео: {escape_markdown(video['title'])}",
                reply_markup=get_video_keyboard(video["video_url"]),
                parse_mode="MarkdownV2",
            )

        await message.reply("Видео успешно сохранены!", parse_mode="MarkdownV2")
    except ValueError as ve:
        logging.error(f"Ошибка: {ve}")
        await message.reply(
            f"Ошибка: {escape_markdown(str(ve))}", parse_mode="MarkdownV2"
        )
    except Exception as e:
        logging.error(f"Ошибка при обработке команды: {e}")
        await message.reply(
            "Ошибка при обработке команды. Проверьте правильность ввода.",
            parse_mode="MarkdownV2",
        )


async def list_videos_handler(message: types.Message, db: AsyncSession):
    try:
        logging.info(f"Получено сообщение: {message.text}")
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError(
                "Неверный формат команды. Используйте: /list <название канала>"
            )
        _, channel_name = parts
        logging.info(f"Получение списка видео для канала: {channel_name}")

        videos = await video_repo.get_videos_by_channel(db, channel_name)
        if videos:
            for video in videos:
                await message.reply(
                    f"Название: {escape_markdown(video.title)}\n"
                    f"Описание: {escape_markdown(video.description)}\n"
                    f"Просмотры: {escape_markdown(video.views)}\n"
                    f"Ссылка: {escape_markdown(video.video_url)}",
                    parse_mode="MarkdownV2",
                )
        else:
            await message.reply(
                "Видео не найдены для указанного канала.", parse_mode="MarkdownV2"
            )
    except ValueError as ve:
        logging.error(f"Ошибка: {ve}")
        await message.reply(
            f"Ошибка: {escape_markdown(str(ve))}", parse_mode="MarkdownV2"
        )
    except Exception as e:
        logging.error(f"Ошибка при обработке команды: {e}")
        await message.reply(
            "Ошибка при обработке команды. Проверьте правильность ввода.",
            parse_mode="MarkdownV2",
        )


async def video_details_handler(callback_query: CallbackQuery, db: AsyncSession):
    video_id = callback_query.data.split("_")[1]
    video = await video_repo.get_video_by_id(db, video_id)
    if video:
        await callback_query.message.reply(
            f"Название: {escape_markdown(video.title)}\n"
            f"Описание: {escape_markdown(video.description)}\n"
            f"Просмотры: {escape_markdown(video.views)}\n"
            f"Ссылка: {escape_markdown(video.video_url)}",
            parse_mode="MarkdownV2",
        )
    else:
        await callback_query.message.reply("Видео не найдено.", parse_mode="MarkdownV2")


def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command(commands=["start"]))
    dp.message.register(parse_handler, Command(commands=["parse"]))
    dp.message.register(list_videos_handler, Command(commands=["list"]))
    dp.callback_query.register(
        video_details_handler, lambda c: c.data.startswith("details_")
    )

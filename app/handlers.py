import logging
from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.services.parsing_service import ParserService
from app.services.db_saving_service import SavingService
from app.repositories.video_repository import VideoRepository
from app.keyboards import get_video_keyboard, get_channel_keyboard
from sqlalchemy.ext.asyncio import AsyncSession

video_repo = VideoRepository()
saving_service = SavingService(video_repo)


class ParseStates(StatesGroup):
    waiting_for_channel_url = State()
    waiting_for_video_count = State()


class ListStates(StatesGroup):
    waiting_for_channel_name = State()


async def start_handler(message: types.Message):
    logging.info("Запуск бота")
    await message.reply(
        "Привет! Вставьте ссылку на канал RUTUBE и укажите количество видео для парсинга.\n"
        "Примеры команд:\n"
        "/parse - Начать парсинг видео\n"
        "/list - Получить список видео"
    )


async def parse_start(message: types.Message, state: FSMContext):
    logging.info("Начало парсинга")
    await message.answer("Введите URL канала:")
    await state.set_state(ParseStates.waiting_for_channel_url)


async def parse_channel_url(message: types.Message, state: FSMContext):
    logging.info(f"Получен URL канала: {message.text}")
    await state.update_data(channel_url=message.text)
    await message.answer("Введите количество видео для парсинга:")
    await state.set_state(ParseStates.waiting_for_video_count)


async def parse_video_count(
    message: types.Message, state: FSMContext, db: AsyncSession
):
    data = await state.get_data()
    channel_url = data["channel_url"]
    video_count = int(message.text)
    logging.info(f"Парсинг канала: {channel_url} для {video_count} видео")

    if not channel_url.startswith(("http://", "https://")):
        channel_url = "http://" + channel_url

    logging.info(f"Окончательный URL канала для парсинга: {channel_url}")

    try:
        videos = await ParserService.parse_channel(channel_url, video_count)
        await saving_service.save_videos(db, videos)

        for video in videos:
            await message.reply(
                f"Сохранено видео: <b>{video['title']}</b>",
                reply_markup=get_video_keyboard(video["video_url"]),
                parse_mode="HTML",
            )

        await message.answer("Видео успешно сохранены!", parse_mode="HTML")
    except Exception as e:
        logging.error(f"Ошибка при парсинге: {e}")
        error_message = f"Ошибка при парсинге: {str(e)}"
        await message.reply(error_message, parse_mode="HTML")
    await state.clear()


async def list_start(message: types.Message, state: FSMContext):
    logging.info("Запрос списка видео")
    await message.answer("Введите название канала:")
    await state.set_state(ListStates.waiting_for_channel_name)


async def list_channel_name(
    message: types.Message, state: FSMContext, db: AsyncSession
):
    channel_name = message.text
    logging.info(f"Получение списка видео для канала: {channel_name}")
    videos = await video_repo.get_videos_by_channel(db, channel_name)
    if videos:
        await message.answer(
            "Выберите видео:", reply_markup=get_channel_keyboard(videos)
        )
    else:
        await message.answer("Видео не найдены для указанного канала.")
    await state.clear()


async def video_details_handler(callback_query: CallbackQuery, db: AsyncSession):
    try:
        video_id = int(callback_query.data.split("_")[1])
        video = await video_repo.get_video_by_id(db, video_id)
        if video:
            logging.info(f"Показ деталей видео: {video.title}")
            await callback_query.message.reply(
                f"Название: <b>{video.title}</b>\n"
                f"Описание: <i>{video.description}</i>\n"
                f"Просмотры: <b>{video.views}</b>\n"
                f"Ссылка: <a href='{video.video_url}'>Смотреть видео</a>",
                parse_mode="HTML",
            )
        else:
            logging.error("Видео не найдено или найдено несколько записей")
            await callback_query.message.reply(
                "Видео не найдено или найдено несколько записей.",
                parse_mode="HTML",
            )
    except ValueError:
        logging.error("Некорректный ID видео")
        await callback_query.message.reply("Некорректный ID видео.", parse_mode="HTML")
    except Exception as e:
        logging.error(f"Ошибка при обработке команды: {e}")
        await callback_query.message.reply(
            "Произошла ошибка при обработке команды.", parse_mode="HTML"
        )


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

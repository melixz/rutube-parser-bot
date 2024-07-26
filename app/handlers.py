import logging
from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.services.parsing_service import ParserService
from app.services.db_saving_service import SavingService
from app.repositories.video_repository import VideoRepository
from app.repositories.user_repository import UserRepository
from app.keyboards import (
    get_video_keyboard,
    get_channel_keyboard,
    get_channel_names_keyboard,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User

video_repo = VideoRepository()
user_repo = UserRepository()
saving_service = SavingService(video_repo)


class ParseStates(StatesGroup):
    waiting_for_channel_url = State()
    waiting_for_video_count = State()


class ListStates(StatesGroup):
    waiting_for_channel_name = State()


class InitStates(StatesGroup):
    initialized = State()


async def start_handler(message: types.Message, state: FSMContext, db: AsyncSession):
    logging.info("Запуск бота")
    telegram_user_id = message.from_user.id

    user = await user_repo.get_user_by_telegram_id(db, telegram_user_id)

    if not user:
        new_user = User(telegram_user_id=telegram_user_id)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        user = new_user

    await state.set_state(InitStates.initialized)
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
    telegram_user_id = message.from_user.id

    logging.info(f"Парсинг канала: {channel_url} для {video_count} видео")

    if not channel_url.startswith(("http://", "https://")):
        channel_url = "http://" + channel_url

    logging.info(f"Окончательный URL канала для парсинга: {channel_url}")

    try:
        videos = await ParserService.parse_channel(channel_url, video_count)

        if not videos:
            await message.reply("На канале больше нет видео для парсинга.")
            await state.clear()
            return

        if len(videos) < video_count:
            await message.reply(
                f"На канале недостаточно видео. Найдено только {len(videos)} видео(ов)."
            )
            await state.clear()
            return

        saved_videos = []
        user = await user_repo.get_user_by_telegram_id(db, telegram_user_id)
        for video in videos:
            video_exists = await video_repo.get_video_by_url(db, video["video_url"])
            if video_exists:
                logging.info(
                    f"Видео с URL {video['video_url']} уже существует в базе данных."
                )
                await message.reply(
                    f"Видео с URL {video['video_url']} уже существует в базе данных."
                )
            else:
                video_data = {
                    "title": video["title"],
                    "description": video["description"],
                    "views": video["views"],
                    "video_url": video["video_url"],
                    "channel_name": video["channel_name"],
                    "user_id": user.id,
                }
                await saving_service.save_videos(db, [video_data], user.id)
                saved_videos.append(video)
                logging.info(f"Сохранено видео: {video['title']}")
                await message.reply(
                    f"<b>Сохранено видео:</b> {video['title']}\n"
                    f"<b>Описание:</b> {video['description']}\n"
                    f"<b>Просмотры:</b> {video['views']}\n",
                    reply_markup=get_video_keyboard(video["video_url"]),
                    parse_mode="HTML",
                )

        if saved_videos:
            await message.answer("Видео успешно сохранены!")
        else:
            await message.answer(
                "Ни одно из видео не было сохранено, так как все они уже существуют в базе данных."
            )
    except Exception as e:
        logging.error(f"Ошибка при парсинге: {e}")
        error_message = (
            f"Ошибка при парсинге: {str(e).replace('<', '').replace('>', '')}"
        )
        await message.reply(error_message)
    await state.clear()


async def list_start(message: types.Message, state: FSMContext, db: AsyncSession):
    logging.info("Запрос списка видео")
    telegram_user_id = message.from_user.id
    user = await user_repo.get_user_by_telegram_id(db, telegram_user_id)
    if not user:
        await message.answer("Пользователь не найден.")
        return
    channel_names = await video_repo.get_unique_channel_names_by_user(db, user.id)
    if channel_names:
        await message.answer(
            "Выберите канал:", reply_markup=get_channel_names_keyboard(channel_names)
        )
    else:
        await message.answer("Каналы не найдены.")


async def list_channel_name(
    message: types.Message, state: FSMContext, db: AsyncSession
):
    telegram_user_id = message.from_user.id
    user = await user_repo.get_user_by_telegram_id(db, telegram_user_id)
    channel_name = message.text
    logging.info(f"Получение списка видео для канала: {channel_name}")
    videos = await video_repo.get_videos_by_channel_and_user(db, channel_name, user.id)
    if videos:
        await message.answer(
            "Выберите видео:", reply_markup=get_channel_keyboard(videos)
        )
    else:
        await message.answer("Видео не найдены для указанного канала.")
    await state.clear()


async def video_details_handler(callback_query: CallbackQuery, db: AsyncSession):
    telegram_user_id = callback_query.from_user.id
    user = await user_repo.get_user_by_telegram_id(db, telegram_user_id)
    try:
        video_id = int(callback_query.data.split("_")[1])
        video = await video_repo.get_video_by_id(db, video_id, user.id)
        if video:
            logging.info(f"Показ деталей видео: {video.title}")
            await callback_query.message.reply(
                f"Название: <b>{video.title}</b>\n"
                f"Описание: <i>{video.description}</i>\n"
                f"Просмотры: <b>{video.views}</b>\n",
                reply_markup=get_video_keyboard(video.video_url),
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


async def handle_all_messages(
    message: types.Message, state: FSMContext, db: AsyncSession
):
    current_state = await state.get_state()
    if not current_state or current_state == InitStates.initialized.state:
        await start_handler(message, state, db)
    else:
        await message.answer(
            "Пожалуйста, используйте команду /start для начала работы с ботом."
        )


async def channel_selection_handler(callback_query: CallbackQuery, db: AsyncSession):
    telegram_user_id = callback_query.from_user.id
    user = await user_repo.get_user_by_telegram_id(db, telegram_user_id)
    short_channel_id = callback_query.data.split("_")[1]
    channel_name = get_channel_name_by_short_id(short_channel_id)
    logging.info(f"Получение списка видео для канала: {channel_name}")
    videos = await video_repo.get_videos_by_channel_and_user(db, channel_name, user.id)
    if videos:
        await callback_query.message.answer(
            "Выберите видео:", reply_markup=get_channel_keyboard(videos)
        )
    else:
        await callback_query.message.answer("Видео не найдены для указанного канала.")


def get_channel_name_by_short_id(short_channel_id):
    channel_mapping = {
        "3e1d91f6c2d2b4b6": "Байки Страха † Страшные истории на ночь",
    }
    return channel_mapping.get(short_channel_id, "Неизвестный канал")


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

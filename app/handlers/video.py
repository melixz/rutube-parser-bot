from aiogram import Router, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.video_repository import VideoRepository
from app.repositories.user_repository import UserRepository
from app.keyboards import get_video_keyboard, get_channel_keyboard
from app.handlers.utils import get_channel_name_by_short_id
from app.handlers.states import InitStates
from app.handlers.start import start_handler
import logging

video_repo = VideoRepository()
user_repo = UserRepository()

video_router = Router()


@video_router.callback_query(lambda cb: cb.data.startswith("video_"))
async def video_details_handler(callback_query: CallbackQuery, db: AsyncSession):
    telegram_user_id = callback_query.from_user.id
    user = await user_repo.get_user_by_telegram_id(db, telegram_user_id)
    try:
        video_id = int(callback_query.data.split("_")[1])
        video = await video_repo.get_video_by_id(db, video_id, user.id)
        if video:
            logging.info(f"Video details: {video}")
            await callback_query.message.reply(
                f"Название: <b>{video.title}</b>\n"
                f"Описание: <i>{video.description}</i>\n"
                f"Просмотры: <b>{video.views}</b>\n",
                reply_markup=get_video_keyboard(video),
                parse_mode="HTML",
            )
        else:
            await callback_query.message.reply(
                "Видео не найдено или найдено несколько записей.", parse_mode="HTML"
            )
    except ValueError:
        await callback_query.message.reply("Некорректный ID видео.", parse_mode="HTML")
    except Exception as e:
        logging.error(f"Error in video_details_handler: {e}")
        await callback_query.message.reply(
            "Произошла ошибка при обработке команды.", parse_mode="HTML"
        )


@video_router.message(InitStates.initialized)
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


@video_router.callback_query(lambda cb: cb.data.startswith("channel_"))
async def channel_selection_handler(callback_query: CallbackQuery, db: AsyncSession):
    telegram_user_id = callback_query.from_user.id
    user = await user_repo.get_user_by_telegram_id(db, telegram_user_id)

    callback_data = callback_query.data
    logging.info(f"Callback data: {callback_data}")

    short_channel_id = callback_data.split("_")[1]
    channel_name = await get_channel_name_by_short_id(db, short_channel_id, user.id)

    logging.info(f"Short channel ID: {short_channel_id}")
    logging.info(f"Channel name: {channel_name}")

    videos = await video_repo.get_videos_by_channel_and_user(db, channel_name, user.id)
    if videos:
        for video in videos:
            logging.info(f"Video ID: {video.id}, Video URL: {video.video_url}")
        await callback_query.message.answer(
            "Выберите видео:", reply_markup=get_channel_keyboard(videos)
        )
    else:
        await callback_query.message.answer("Видео не найдены для указанного канала.")

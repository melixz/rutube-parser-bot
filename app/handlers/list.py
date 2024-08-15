from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.video_repository import VideoRepository
from app.repositories.user_repository import UserRepository
from app.keyboards import get_channel_names_keyboard, get_channel_keyboard
from app.handlers.states import ListStates

video_repo = VideoRepository()
user_repo = UserRepository()

list_router = Router()


@list_router.message(lambda message: message.text.startswith("/list_start"))
async def list_start(message: types.Message, state: FSMContext, db: AsyncSession):
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
        await state.set_state(ListStates.waiting_for_channel_name)
    else:
        await message.answer("Каналы не найдены.")


@list_router.message(ListStates.waiting_for_channel_name)
async def list_channel_name(
    message: types.Message, state: FSMContext, db: AsyncSession
):
    telegram_user_id = message.from_user.id
    user = await user_repo.get_user_by_telegram_id(db, telegram_user_id)
    channel_name = message.text
    videos = await video_repo.get_videos_by_channel_and_user(db, channel_name, user.id)
    if videos:
        await message.answer(
            "Выберите видео:", reply_markup=get_channel_keyboard(videos)
        )
    else:
        await message.answer("Видео не найдены для указанного канала.")
    await state.clear()

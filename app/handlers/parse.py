from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.parsing_service import ParserService
from app.services.db_saving_service import SavingService
from app.repositories.video_repository import VideoRepository
from app.repositories.user_repository import UserRepository
from app.keyboards import get_video_keyboard
from app.handlers.states import ParseStates

video_repo = VideoRepository()
user_repo = UserRepository()
saving_service = SavingService(video_repo)

parse_router = Router()


@parse_router.message(commands=["parse_start"])
async def parse_start(message: types.Message, state: FSMContext):
    await message.answer("Введите URL канала:")
    await state.set_state(ParseStates.waiting_for_channel_url)


@parse_router.message(state=ParseStates.waiting_for_channel_url)
async def parse_channel_url(message: types.Message, state: FSMContext):
    await state.update_data(channel_url=message.text)
    await message.answer("Введите количество видео для парсинга:")
    await state.set_state(ParseStates.waiting_for_video_count)


@parse_router.message(state=ParseStates.waiting_for_video_count)
async def parse_video_count(
    message: types.Message, state: FSMContext, db: AsyncSession
):
    data = await state.get_data()
    channel_url = data["channel_url"]
    video_count = int(message.text)
    telegram_user_id = message.from_user.id

    if not channel_url.startswith(("http://", "https://")):
        channel_url = "http://" + channel_url

    try:
        videos = await ParserService.parse_channel(channel_url, video_count)
        user = await user_repo.get_user_by_telegram_id(db, telegram_user_id)
        saved_videos = []

        for video in videos:
            video_exists = await video_repo.get_video_by_url(db, video["video_url"])
            if video_exists:
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
        await message.reply(
            f"Ошибка при парсинге: {str(e).replace('<', '').replace('>', '')}"
        )
    await state.clear()

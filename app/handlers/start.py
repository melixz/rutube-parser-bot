from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.handlers.states import InitStates

user_repo = UserRepository()


async def start_handler(message: types.Message, state: FSMContext, db: AsyncSession):
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

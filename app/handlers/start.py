from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.handlers.states import InitStates

user_repo = UserRepository()
start_router = Router()


@start_router.message(lambda message: message.text.startswith("/start"))
async def start_handler(message: types.Message, state: FSMContext, db: AsyncSession):
    telegram_user_id = message.from_user.id
    user = await user_repo.get_user_by_telegram_id(db, telegram_user_id)

    if not user:
        new_user = User(telegram_user_id=telegram_user_id)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        user = new_user

    await state.clear()
    await state.set_state(InitStates.initialized)
    await message.reply(
        "Привет! Вставьте ссылку на канал RUTUBE и укажите количество видео для парсинга.\n"
        "Примеры команд:\n"
        "/parse - Начать парсинг видео\n"
        "/list - Получить список видео"
    )


@start_router.message()
async def handle_all_messages(
    message: types.Message, state: FSMContext, db: AsyncSession
):
    current_state = await state.get_state()

    if current_state != InitStates.initialized.state:
        reminded = await state.get_data()
        if not reminded.get("reminded"):
            await message.answer(
                "Пожалуйста, используйте команду /start для начала работы с ботом."
            )
            await state.update_data(reminded=True)
        else:
            await start_handler(message, state, db)
    else:
        await start_handler(message, state, db)

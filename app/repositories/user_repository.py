from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.user import User


class UserRepository:
    async def get_user_by_telegram_id(self, db: AsyncSession, telegram_user_id: int):
        result = await db.execute(
            select(User).where(User.telegram_user_id == telegram_user_id)
        )
        return result.scalar_one_or_none()

    async def add_user(self, db: AsyncSession, telegram_user_id: int):
        new_user = User(telegram_user_id=telegram_user_id)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

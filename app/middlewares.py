from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker):
        self.sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.sessionmaker() as session:
            data["db"] = session
            return await handler(event, data)

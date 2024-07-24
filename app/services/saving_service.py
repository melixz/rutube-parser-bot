from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Video


class SavingService:
    @staticmethod
    async def save_videos(videos: list[dict], db: AsyncSession):
        for video in videos:
            db_video = Video(**video)
            db.add(db_video)
        await db.commit()

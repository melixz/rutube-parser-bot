from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Video


class VideoRepository:

    @staticmethod
    async def add_video(db: AsyncSession, video_data: dict):
        video = Video(**video_data)
        db.add(video)
        await db.commit()
        return video

    @staticmethod
    async def get_videos_by_channel(db: AsyncSession, channel_id: str):
        result = await db.execute(select(Video).where(Video.channel_id == channel_id))
        return result.scalars().all()

    @staticmethod
    async def get_video_by_id(db: AsyncSession, video_id: int):
        result = await db.execute(select(Video).where(Video.id == video_id))
        return result.scalar()

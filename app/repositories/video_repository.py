from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.video import Video


class VideoRepository:
    async def add_video(self, db: AsyncSession, video: Video):
        db.add(video)
        await db.commit()
        await db.refresh(video)
        return video

    async def get_videos_by_channel(self, db: AsyncSession, channel_name: str):
        result = await db.execute(
            select(Video).filter(Video.channel_name == channel_name)
        )
        return result.scalars().all()

    async def get_video_by_id(self, db: AsyncSession, video_id: str):
        result = await db.execute(
            select(Video).filter(Video.video_url.like(f"%{video_id}%"))
        )
        return result.scalar_one_or_none()

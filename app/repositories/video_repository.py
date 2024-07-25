from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.video import Video


class VideoRepository:
    async def get_video_by_id(self, db: AsyncSession, video_id: int):
        result = await db.execute(select(Video).where(Video.id == video_id))
        return result.scalar_one_or_none()

    async def get_videos_by_channel(self, db: AsyncSession, channel_name: str):
        result = await db.execute(
            select(Video).where(Video.channel_name == channel_name)
        )
        return result.scalars().all()

    async def add_video(self, db: AsyncSession, video_data: dict):
        new_video = Video(**video_data)
        db.add(new_video)
        await db.commit()
        await db.refresh(new_video)
        return new_video

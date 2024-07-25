from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.video import Video


class VideoRepository:
    async def add_video(self, db: AsyncSession, video: Video):
        async with db.begin():
            db.add(video)
            await db.commit()
            await db.refresh(video)
            return video

    async def get_video_by_id(self, db: AsyncSession, video_id: int):
        async with db.begin():
            result = await db.execute(select(Video).filter(Video.id == video_id))
            return result.scalars().first()

    async def get_videos_by_channel(self, db: AsyncSession, channel_name: str):
        async with db.begin():
            result = await db.execute(
                select(Video).filter(Video.channel_name == channel_name)
            )
            return result.scalars().all()

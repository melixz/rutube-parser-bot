from sqlalchemy.future import select
from app.db.session import async_session
from app.db.models.video import Video


class VideoRepository:
    async def add_video(self, video: Video):
        async with async_session() as session:
            session.add(video)
            await session.commit()
            await session.refresh(video)
            return video

    async def get_video_by_id(self, video_id: int):
        async with async_session() as session:
            result = await session.execute(select(Video).filter(Video.id == video_id))
            return result.scalars().first()

    async def get_videos_by_channel(self, channel_name: str):
        async with async_session() as session:
            result = await session.execute(
                select(Video).filter(Video.channel_name == channel_name)
            )
            return result.scalars().all()

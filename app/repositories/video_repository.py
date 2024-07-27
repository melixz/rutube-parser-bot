from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.video import Video
import hashlib


class VideoRepository:
    async def get_video_by_id(self, db: AsyncSession, video_id: int, user_id: int):
        result = await db.execute(
            select(Video).where(Video.id == video_id, Video.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_videos_by_channel_and_user(
        self, db: AsyncSession, channel_name: str, user_id: int
    ):
        result = await db.execute(
            select(Video).where(
                Video.channel_name == channel_name, Video.user_id == user_id
            )
        )
        return result.scalars().all()

    async def add_video(self, db: AsyncSession, video_data: dict):
        new_video = Video(**video_data)
        db.add(new_video)
        await db.commit()
        await db.refresh(new_video)
        return new_video

    async def get_video_by_url(self, db: AsyncSession, video_url: str):
        result = await db.execute(select(Video).where(Video.video_url == video_url))
        return result.scalar_one_or_none()

    async def get_unique_channel_names_by_user(self, db: AsyncSession, user_id: int):
        result = await db.execute(
            select(Video.channel_name).where(Video.user_id == user_id).distinct()
        )
        return [row[0] for row in result.all()]

    async def get_videos_by_channel_short_id(
        self, db: AsyncSession, short_channel_id: str, user_id: int
    ):
        result = await db.execute(select(Video).where(Video.user_id == user_id))
        videos = result.scalars().all()
        for video in videos:
            hash_object = hashlib.md5(video.channel_name.encode("utf-8"))
            if hash_object.hexdigest()[:16] == short_channel_id:
                return [video]
        return []

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.video_repository import VideoRepository

video_repo = VideoRepository()


async def get_channel_name_by_short_id(
    db: AsyncSession, short_channel_id: str, user_id: int
):
    videos = await video_repo.get_videos_by_channel_short_id(
        db, short_channel_id, user_id
    )
    if videos:
        return videos[0].channel_name
    return "Неизвестный канал"

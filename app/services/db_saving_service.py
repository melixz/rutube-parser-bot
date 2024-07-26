from app.repositories.video_repository import VideoRepository
from sqlalchemy.ext.asyncio import AsyncSession


class SavingService:
    def __init__(self, video_repo: VideoRepository):
        self.video_repo = video_repo

    async def save_videos(self, db, videos: list, user_id: int):
        for video_data in videos:
            video_url = video_data.get("video_url")
            existing_video = await self.video_repo.get_video_by_url(db, video_url)
            if existing_video:
                print(f"Video with URL {video_url} already exists in the database.")
                continue
            video_data["user_id"] = user_id
            await self.video_repo.add_video(db, video_data)

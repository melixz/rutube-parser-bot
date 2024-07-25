from app.repositories.video_repository import VideoRepository


class SavingService:
    def __init__(self, video_repo: VideoRepository):
        self.video_repo = video_repo

    async def save_videos(self, db, videos: list):
        for video_data in videos:
            await self.video_repo.add_video(db, video_data)

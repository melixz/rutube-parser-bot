from app.repositories.video_repository import VideoRepository
from app.db.models.video import Video


class SavingService:

    def __init__(self, video_repo: VideoRepository):
        self.video_repo = video_repo

    async def save_videos(self, db, videos: list):
        for video_data in videos:
            video = Video(
                title=video_data["title"],
                description=video_data["description"],
                views=video_data["views"],
                video_url=video_data["video_url"],
                channel_name=video_data["channel_name"],
            )
            await self.video_repo.add_video(db, video)

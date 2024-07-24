from app.repositories.video_repository import VideoRepository
from app.db.models.video import Video


class SavingService:
    """Сервис по сохранению данных в db."""

    def __init__(self, video_repo: VideoRepository):
        self.video_repo = video_repo

    async def save_videos(self, db, videos: list):
        """Сохраняет видео в базу данных."""
        for video_data in videos:
            video = Video(
                title=video_data["title"],
                description=video_data["description"],
                views=video_data["views"],
                url=video_data["video_url"],
                channel_id=video_data[
                    "channel_name"
                ],  # Используем channel_name в качестве channel_id
            )
            await self.video_repo.add_video(db, video)

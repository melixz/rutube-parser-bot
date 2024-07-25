from app.repositories.video_repository import VideoRepository


class SavingService:
    def __init__(self, video_repo: VideoRepository):
        self.video_repo = video_repo

    async def save_videos(self, db, videos: list):
        for video_data in videos:
            video_url = video_data.get("video_url")
            existing_video = await self.video_repo.get_video_by_url(db, video_url)
            if existing_video:
                print(f"Video with URL {video_url} already exists in the database.")
                continue
            await self.video_repo.add_video(db, video_data)

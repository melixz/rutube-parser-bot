import httpx
from bs4 import BeautifulSoup


class ParsingService:
    @staticmethod
    async def fetch_videos(channel_url: str, video_count: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(channel_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            videos = []
            video_elements = soup.find_all('div', class_='video-element', limit=video_count)
            for video in video_elements:
                title = video.find('h3').text
                description = video.find('p').text[:100]
                views = int(video.find('span', class_='views').text)
                url = video.find('a')['href']
                videos.append({
                    'title': title,
                    'description': description,
                    'views': views,
                    'url': url
                })
            return videos

import httpx
from bs4 import BeautifulSoup

MAX_DESCRIPTION = 97


class ParserService:
    @staticmethod
    async def parse_channel(channel_url: str, video_count: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(channel_url)
            if response.status_code == 301:
                redirected_url = response.headers["Location"]
                response = await client.get(redirected_url)
            if response.status_code != 200:
                raise Exception(
                    f"Ошибка получения данных с канала. Статус ошибки: {response.status_code}"
                )
            soup = BeautifulSoup(response.text, "html.parser")
            videos = []
            video_elements = soup.select(
                "a.wdp-link-module__link.wdp-card-poster-module__posterWrapper"
            )
            for video in video_elements[:video_count]:
                video_url = f'https://rutube.ru{video["href"]}'
                video_response = await client.get(video_url)
                video_soup = BeautifulSoup(video_response.text, "html.parser")
                video_title = video_soup.find(
                    "section", class_="video-pageinfo-container-module__videoTitle"
                ).text.strip()
                video_description = (
                    video_soup.find(
                        "div",
                        class_="freyja_pen-videopage-description__description_x8Lqk",
                    ).text.strip()[:MAX_DESCRIPTION]
                    + "..."
                )
                video_views = (
                    video_soup.find(
                        "div",
                        class_="wdp-video-options-row-module__wdpVideoOptionsRow__views-count",
                    )
                    .text.strip()
                    .replace("\xa0", " ")
                )
                channel_name = video_soup.find(
                    "span",
                    class_="freyja_pen-author-options-row__pen-author-options-row__author-title_NEF8H",
                ).text.strip()
                videos.append(
                    {
                        "title": video_title,
                        "description": video_description,
                        "views": video_views,
                        "video_url": video_url,
                        "channel_name": channel_name,
                    }
                )
            return videos

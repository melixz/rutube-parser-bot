import logging
import httpx
from bs4 import BeautifulSoup

MAX_DESCRIPTION: int = 100


class ParserService:
    @staticmethod
    async def parse_channel(channel_url: str, video_count: int):
        if not channel_url.startswith(("http://", "https://")):
            channel_url = "http://" + channel_url

        logging.info(f"Окончательный URL канала для парсинга: {channel_url}")

        async with httpx.AsyncClient(follow_redirects=True) as client:
            chanal_response = await client.get(channel_url)
            if chanal_response.status_code != 200:
                raise Exception(
                    "Ошибка получения данных с канала. "
                    f"Статус ошибки: {chanal_response.status_code}"
                )
            chanal_soup = BeautifulSoup(chanal_response.text, "html.parser")
            chanal_videos = chanal_soup.select(
                "a.wdp-link-module__link.wdp-card-poster-module__posterWrapper"
            )
            videos = []
            for video in chanal_videos[:video_count]:
                video_url = f'https://rutube.ru{video["href"]}'
                video_response = await client.get(video_url)
                video_soup = BeautifulSoup(video_response.text, "html.parser")
                video_title_tag = video_soup.find(
                    "section", class_="video-pageinfo-container-module__videoTitle"
                )
                video_title = (
                    video_title_tag.text.strip() if video_title_tag else "Нет названия"
                )

                video_description_tag = video_soup.find(
                    "div",
                    class_=("freyja_pen-videopage-description__description_x8Lqk"),
                )
                video_description = (
                    video_description_tag.text.strip()[:MAX_DESCRIPTION] + "..."
                    if video_description_tag
                    else "Нет описания"
                )

                video_views_tag = video_soup.find(
                    "div",
                    class_=(
                        "wdp-video-options-row-module__wdpVideoOptionsRow__views-count"
                    ),
                )
                video_views = (
                    video_views_tag.text.strip()
                    if video_views_tag
                    else "Нет просмотров"
                )

                channel_name_tag = video_soup.find(
                    "span",
                    class_=(
                        "freyja_pen-author-options-row__pen-author-options-row__author-title_NEF8H"
                    ),
                )
                channel_name = (
                    channel_name_tag.text.strip() if channel_name_tag else "Нет канала"
                )

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

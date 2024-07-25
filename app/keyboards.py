from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_video_keyboard(video_url: str):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Посмотреть видео", url=video_url)]]
    )
    return keyboard


def get_channel_keyboard(videos):
    inline_keyboard = []
    for video in videos:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=video.title, callback_data=f"details_{video.id}"
                )
            ]
        )
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard

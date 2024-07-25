from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_video_keyboard(video_url: str):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Посмотреть видео", url=video_url)]]
    )
    return keyboard

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


def get_channel_names_keyboard(channel_names):
    inline_keyboard = []
    for channel_name in channel_names:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=channel_name, callback_data=f"channel_{channel_name}"
                )
            ]
        )
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard

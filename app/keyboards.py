from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_video_keyboard(video_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="Подробнее", callback_data=f"details_{video_id}")
    )
    return keyboard

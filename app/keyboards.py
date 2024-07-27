from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import hashlib


def get_video_keyboard(video):
    if isinstance(video, str):
        logging.error(f"Expected a video object, but got a string: {video}")
        return InlineKeyboardMarkup(inline_keyboard=[[]])
    else:
        logging.info(f"Creating keyboard for video URL: {video.video_url}")
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Посмотреть видео", url=video.video_url)]
            ]
        )
    return keyboard


def get_channel_keyboard(videos):
    inline_keyboard = []
    for video in videos:
        callback_data = f"details_{video.id}"
        logging.info(
            f"Callback data for video {video.title}: {callback_data} (Length: {len(callback_data.encode('utf-8'))})"
        )
        if len(callback_data.encode("utf-8")) > 64:
            raise ValueError("Callback data length exceeds 64 bytes")
        inline_keyboard.append(
            [InlineKeyboardButton(text=video.title, callback_data=callback_data)]
        )
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


def get_channel_names_keyboard(channel_names):
    inline_keyboard = []
    for channel_name in channel_names:
        hash_object = hashlib.md5(channel_name.encode("utf-8"))
        short_channel_id = hash_object.hexdigest()[:16]
        callback_data = f"channel_{short_channel_id}"
        logging.info(
            f"Callback data for channel {channel_name}: {callback_data} (Length: {len(callback_data.encode('utf-8'))})"
        )
        if len(callback_data.encode("utf-8")) > 64:
            raise ValueError("Callback data length exceeds 64 bytes")
        inline_keyboard.append(
            [InlineKeyboardButton(text=channel_name, callback_data=callback_data)]
        )
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard

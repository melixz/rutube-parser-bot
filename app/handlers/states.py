from aiogram.fsm.state import StatesGroup, State


class ParseStates(StatesGroup):
    waiting_for_channel_url = State()
    waiting_for_video_count = State()


class ListStates(StatesGroup):
    waiting_for_channel_name = State()


class InitStates(StatesGroup):
    initialized = State()

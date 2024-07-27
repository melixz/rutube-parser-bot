def get_channel_name_by_short_id(short_channel_id):
    channel_mapping = {
        "3e1d91f6c2d2b4b6": "Байки Страха † Страшные истории на ночь",
    }
    return channel_mapping.get(short_channel_id, "Неизвестный канал")

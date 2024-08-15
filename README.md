# rutube-parser-bot

## Описание проекта

`rutube-parser-bot` - это Telegram-бот, который позволяет пользователям парсить видео с каналов на видеохостинге RUTUBE. Пользователи могут получать информацию о видео, сохранять её в базе данных и просматривать сохранённые видео позже. Бот поддерживает взаимодействие через удобные команды и встроенную клавиатуру.

## Установка

```bash
git clone https://github.com/melixz/rutube-parser-bot
cd rutube-parser-bot
pip install -r requirements.txt
```

## Использование

1. Настройте переменные окружения:

   ```sh
   export BOT_TOKEN=ваш_telegram_token
   export DATABASE_URL=postgresql+asyncpg://ваш_url_базы_данных
   ```

2. Запустите Docker контейнер:

   ```sh
   docker-compose up --build
   ```

3. Начните взаимодействовать с ботом в Telegram.

## Технологии

- Python 3.9+
- aiogram: для создания Telegram-бота
- SQLAlchemy: для работы с базой данных
- httpx: для асинхронных HTTP-запросов
- BeautifulSoup: для парсинга HTML
- PostgreSQL: в качестве базы данных
- Alembic: для управления миграциями базы данных
- Docker и Docker-compose: для контейнеризации приложения

## Текущие возможности

- Парсинг видео с каналов RUTUBE по заданной ссылке
- Сохранение информации о видео в базе данных
- Просмотр сохранённых видео через встроенную клавиатуру
- Получение детальной информации о видео

## Команды

- `/start` - Запуск бота
- `/parse` - Парсинг видео
- `/list` - Список видео

## Цель проекта

Код написан для автоматизации парсинга видео с RUTUBE и предоставления удобного интерфейса для взаимодействия с пользователями через Telegram.

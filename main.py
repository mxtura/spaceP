import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import API_TOKEN
from bot.handlers import register_handlers
from bot.utils import init_all_cameras, close_drivers  # Импортируем init_driver и close_driver

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция для запуска бота
async def main():
    try:

        # Инициализируем драйвер и открываем страницу с видеопотоком
        init_all_cameras()

        # Регистрация хэндлеров
        register_handlers(dp)

        # Запуск бота
        await dp.start_polling(bot)
    finally:
        # Закрываем драйвер Selenium при завершении работы бота
        close_drivers()


if __name__ == '__main__':
    asyncio.run(main())

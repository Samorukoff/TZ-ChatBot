import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from app.handlers import router

# Загружаем переменные окружения
load_dotenv()

# Запуск бота
async def main():
    TOKEN = os.getenv("TOKEN")
    bot = Bot(token = TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

# Запускаем только тогда, когда скрипт не импортирован (запущен как программа)
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
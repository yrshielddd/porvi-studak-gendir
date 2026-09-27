import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from db.database import db
from bot.handlers import setup_routers
from services.publisher import Publisher
import services.publisher as publisher_module
from scheduler.jobs import auto_generate_job

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Инициализация
    await db.init()
    publisher_module.publisher = Publisher(bot)

    # Роутеры
    dp.include_router(setup_routers())

    # Планировщик
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        auto_generate_job,
        "interval",
        hours=settings.NEWS_CHECK_HOURS,
        args=[bot],
        id="auto_generate",
    )
    scheduler.start()

    # Первый запуск генерации при старте (опционально)
    # await auto_generate_job(bot)

    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
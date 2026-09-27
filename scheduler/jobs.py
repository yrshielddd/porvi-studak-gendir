from aiogram import Bot
from services.generator import generator
from config import settings


async def auto_generate_job(bot: Bot):
    """Запускается раз в 24 часа"""
    created_ids = await generator.auto_generate()

    if not created_ids:
        return

    text = f"Сгенерировано новых постов: {len(created_ids)}\n"
    text += "ID: " + ", ".join(map(str, created_ids))
    text += "\n\nЗайди в «Список постов»."

    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            pass
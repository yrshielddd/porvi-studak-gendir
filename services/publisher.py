from aiogram import Bot
from config import settings
from db.database import db


class Publisher:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def publish(self, post_id: int) -> bool:
        post = await db.get_post(post_id)
        if not post:
            return False

        try:
            await self.bot.send_message(
                chat_id=settings.CHANNEL_ID,
                text=post.content,
                parse_mode=None,  # чтобы не ломалось на спецсимволах
            )
            await db.update_status(post_id, "published")
            return True
        except Exception as e:
            print(f"Ошибка публикации: {e}")
            return False


# будет инициализирован в main
publisher: Publisher = None
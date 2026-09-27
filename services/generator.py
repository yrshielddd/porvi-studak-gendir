from services.ai import ai
from services.news import news_service
from db.database import db
from typing import Optional


class GeneratorService:
    TOPICS = [
        "лайфхаки по написанию курсовой",
        "что делать если препод заваливает",
        "как пережить сессию без нервного срыва",
        "типичные ошибки в дипломе",
        "как правильно общаться с научником",
        "прокрастинация и дедлайны",
        "как выбрать тему курсовой",
        "студенческие мифы",
        "что делать если не успеваешь сдать работу",
        "как не сгореть на учёбе",
    ]

    async def generate_regular_post(self) -> int:
        """Обычный пост (не новость)"""
        import random
        topic = random.choice(self.TOPICS)

        prompt = f"""
ТЕМА: {topic}
ТИП ПОСТА: useful tip / student problem
ЦЕЛЬ: дать практическую пользу + дерзкий живой тон
ОГРАНИЧЕНИЯ: не рекламируй сервис слишком прямо, максимум лёгкий намёк в конце если уместно.
Напиши готовый пост для Telegram.
"""
        content = await ai.generate(prompt)
        post_id = await db.add_post(content=content, post_type="tip", original_prompt=prompt)
        return post_id

    async def generate_news_post(self, news_item: dict) -> Optional[int]:
        prompt = f"""
ТЕМА: Новость для студентов
ТИП ПОСТА: news
ИСХОДНЫЕ ДАННЫЕ:
Заголовок: {news_item['title']}
Кратко: {news_item['summary']}
Ссылка: {news_item['link']}

ЦЕЛЬ: объяснить, что произошло, что это значит для студента и что делать.
Не выдумывай факты. Если информации мало — прямо скажи.
Напиши готовый пост.
"""
        content = await ai.generate(prompt)
        post_id = await db.add_post(
            content=content,
            post_type="news",
            source_url=news_item.get("link"),
            original_prompt=prompt,
        )
        return post_id

    async def generate_from_brief(self, brief: str) -> int:
        prompt = f"""
BRIEF ОТ АДМИНА:
{brief}

Напиши готовый пост строго по этому брифу и system prompt.
"""
        content = await ai.generate(prompt)
        post_id = await db.add_post(content=content, post_type="brief", original_prompt=prompt)
        return post_id

    async def regenerate(self, post_id: int) -> Optional[str]:
        post = await db.get_post(post_id)
        if not post or not post.original_prompt:
            return None

        new_content = await ai.generate(
            post.original_prompt + "\n\nСделай другую версию этого поста. Сохрани смысл, но измени подачу и структуру."
        )
        await db.update_content(post_id, new_content)
        return new_content

    async def auto_generate(self) -> list[int]:
        """Фоновая генерация: приоритет новостям, но не больше 1 новости"""
        created_ids = []

        news_list = await news_service.get_relevant_news(hours=36)
        if news_list:
            # Берём самую свежую
            news_id = await self.generate_news_post(news_list[0])
            if news_id:
                created_ids.append(news_id)

        # Дополнительно обычный пост
        regular_id = await self.generate_regular_post()
        created_ids.append(regular_id)

        return created_ids


generator = GeneratorService()
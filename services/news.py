import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
import httpx


class NewsService:
    # Бесплатные RSS (можно расширять)
    RSS_FEEDS = [
        "https://news.google.com/rss/search?q=Минобрнауки+студенты&hl=ru&gl=RU&ceid=RU:ru",
        "https://news.google.com/rss/search?q=стипендия+студенты&hl=ru&gl=RU&ceid=RU:ru",
        "https://news.google.com/rss/search?q=общежитие+студенты&hl=ru&gl=RU&ceid=RU:ru",
        "https://news.google.com/rss/search?q=сессия+экзамены+студенты&hl=ru&gl=RU&ceid=RU:ru",
    ]

    async def get_relevant_news(self, hours: int = 48) -> List[Dict]:
        """Возвращает свежие релевантные новости"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        news = []

        for url in self.RSS_FEEDS:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:8]:
                    published = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])

                    if published and published < cutoff:
                        continue

                    news.append({
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", "")[:500],
                        "link": entry.get("link", ""),
                        "published": published.isoformat() if published else None,
                    })
            except Exception:
                continue

        # Убираем дубли по заголовку
        seen = set()
        unique = []
        for item in news:
            title = item["title"].lower().strip()
            if title not in seen:
                seen.add(title)
                unique.append(item)

        return unique[:6]


news_service = NewsService()
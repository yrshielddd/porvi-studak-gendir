from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    BOT_TOKEN: str = "СЮДА_ТОКЕН_БОТА"
    CHANNEL_ID: str = "СЮДА_ID_КАНАЛА"          # например -1001234567890
    ADMIN_IDS: List[int] = []                    # твой telegram id

    GROQ_API_KEY: str = "СЮДА_GROQ_API_KEY"

    NEWS_CHECK_HOURS: int = 24
    DB_PATH: str = "data/bot.db"


settings = Settings()
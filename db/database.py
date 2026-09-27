import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from config import settings
from db.models import Post


class Database:
    def __init__(self, db_path: str = settings.DB_PATH):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    post_type TEXT NOT NULL,
                    source_url TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    published_at TEXT,
                    original_prompt TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            await db.commit()

    async def add_post(
        self,
        content: str,
        post_type: str = "auto",
        source_url: Optional[str] = None,
        original_prompt: Optional[str] = None,
    ) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO posts (content, post_type, source_url, status, created_at, original_prompt)
                VALUES (?, ?, ?, 'pending', ?, ?)
                """,
                (content, post_type, source_url, datetime.utcnow().isoformat(), original_prompt),
            )
            await db.commit()
            return cursor.lastrowid

    async def get_pending_posts(self) -> List[Post]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM posts WHERE status = 'pending' ORDER BY created_at ASC"
            )
            rows = await cursor.fetchall()
            return [self._row_to_post(row) for row in rows]

    async def get_post(self, post_id: int) -> Optional[Post]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
            row = await cursor.fetchone()
            return self._row_to_post(row) if row else None

    async def update_status(self, post_id: int, status: str):
        async with aiosqlite.connect(self.db_path) as db:
            published_at = datetime.utcnow().isoformat() if status == "published" else None
            await db.execute(
                "UPDATE posts SET status = ?, published_at = ? WHERE id = ?",
                (status, published_at, post_id),
            )
            await db.commit()

    async def update_content(self, post_id: int, content: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE posts SET content = ? WHERE id = ?",
                (content, post_id),
            )
            await db.commit()

    async def delete_post(self, post_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
            await db.commit()

    def _row_to_post(self, row) -> Post:
        return Post(
            id=row["id"],
            content=row["content"],
            post_type=row["post_type"],
            source_url=row["source_url"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            published_at=datetime.fromisoformat(row["published_at"]) if row["published_at"] else None,
            original_prompt=row["original_prompt"],
        )


db = Database()
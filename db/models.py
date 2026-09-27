from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Post:
    id: Optional[int]
    content: str
    post_type: str          # news / tip / problem / sales / brief / auto
    source_url: Optional[str]
    status: str             # pending / accepted / rejected / published
    created_at: datetime
    published_at: Optional[datetime] = None
    original_prompt: Optional[str] = None
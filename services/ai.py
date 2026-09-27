from groq import AsyncGroq
from config import settings
from prompts.system_prompt import SYSTEM_PROMPT


class AIService:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    async def generate(self, user_prompt: str, system: str = SYSTEM_PROMPT) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.85,
            max_tokens=2048,
        )
        return response.choices[0].message.content.strip()


ai = AIService()
from aiogram import Router, F
from aiogram.types import Message

from bot.keyboards import post_actions, main_menu
from services.generator import generator
from db.database import db
from config import settings

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


@router.message(F.text == "⚡ Сгенерировать пост сейчас")
async def generate_now(message: Message):
    if not is_admin(message.from_user.id):
        return

    await message.answer("Генерирую...")
    post_id = await generator.generate_regular_post()
    post = await db.get_post(post_id)

    await message.answer(
        f"<b>#{post.id}</b> | {post.post_type}\n\n{post.content}",
        reply_markup=post_actions(post.id),
        parse_mode="HTML",
    )
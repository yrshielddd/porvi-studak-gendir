from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards import post_actions, cancel_kb, main_menu
from bot.states import BriefState
from services.generator import generator
from db.database import db
from config import settings

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


@router.message(F.text == "✍️ Написать пост по брифу")
async def brief_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(BriefState.waiting_brief)
    await message.answer(
        "Пришли бриф.\n\nМожно в свободной форме или по шаблону:\n\n"
        "ТЕМА:\nЦЕЛЬ:\nТИП ПОСТА:\nИСХОДНЫЕ ДАННЫЕ:\nCTA:\nОГРАНИЧЕНИЯ:",
        reply_markup=cancel_kb(),
    )


@router.message(F.text == "🚫 Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_menu())


@router.message(BriefState.waiting_brief)
async def brief_process(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await message.answer("Генерирую по брифу...")
    post_id = await generator.generate_from_brief(message.text)
    post = await db.get_post(post_id)
    await state.clear()

    await message.answer(
        f"<b>#{post.id}</b> | brief\n\n{post.content}",
        reply_markup=post_actions(post.id),
        parse_mode="HTML",
    )
    await message.answer("Готово.", reply_markup=main_menu())
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards import post_actions, main_menu
from bot.states import EditState
from db.database import db
from services.generator import generator
from services.publisher import publisher
from config import settings

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


@router.message(F.text == "📋 Список постов")
async def list_posts(message: Message):
    if not is_admin(message.from_user.id):
        return

    posts = await db.get_pending_posts()
    if not posts:
        await message.answer("Очередь пуста. Можно сгенерировать пост вручную.")
        return

    await message.answer(f"В очереди: {len(posts)} пост(ов). Показываю по одному:")

    for post in posts:
        text = f"<b>#{post.id}</b> | {post.post_type}\n\n{post.content}"
        if post.source_url:
            text += f"\n\n🔗 {post.source_url}"
        await message.answer(text, reply_markup=post_actions(post.id), parse_mode="HTML")


@router.callback_query(F.data.startswith("accept:"))
async def accept_post(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    post_id = int(callback.data.split(":")[1])
    await db.update_status(post_id, "accepted")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Пост принят ✅")
    await callback.message.answer("Пост помечен как принятый. Можешь отправить его в канал кнопкой ниже или через список.")


@router.callback_query(F.data.startswith("reject:"))
async def reject_post(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    post_id = int(callback.data.split(":")[1])
    await db.update_status(post_id, "rejected")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Пост отклонён")


@router.callback_query(F.data.startswith("regen:"))
async def regen_post(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    post_id = int(callback.data.split(":")[1])
    await callback.answer("Генерирую новую версию...")
    new_content = await generator.regenerate(post_id)
    if new_content:
        await callback.message.edit_text(
            f"<b>#{post_id}</b> (новая версия)\n\n{new_content}",
            reply_markup=post_actions(post_id),
            parse_mode="HTML",
        )
    else:
        await callback.answer("Не удалось перегенерировать", show_alert=True)


@router.callback_query(F.data.startswith("edit:"))
async def edit_post_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    post_id = int(callback.data.split(":")[1])
    await state.set_state(EditState.waiting_text)
    await state.update_data(post_id=post_id)
    await callback.message.answer("Пришли новый текст поста:")
    await callback.answer()


@router.message(EditState.waiting_text)
async def edit_post_finish(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    post_id = data["post_id"]
    await db.update_content(post_id, message.text)
    await state.clear()
    await message.answer(
        f"Пост #{post_id} обновлён:\n\n{message.text}",
        reply_markup=post_actions(post_id),
    )


@router.callback_query(F.data.startswith("publish:"))
async def publish_post(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    post_id = int(callback.data.split(":")[1])
    success = await publisher.publish(post_id)
    if success:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer("Опубликовано в канал ✅")
    else:
        await callback.answer("Ошибка публикации. Проверь CHANNEL_ID и права бота.", show_alert=True)
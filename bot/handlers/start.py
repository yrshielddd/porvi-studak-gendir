from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from bot.keyboards import main_menu
from config import settings

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


@router.message(CommandStart())
async def cmd_start(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Нет доступа.")
        return

    await message.answer(
        "Бот генерации постов для студенческого канала.\n\n"
        "Выбирай действие:",
        reply_markup=main_menu(),
    )
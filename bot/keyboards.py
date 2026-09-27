from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Список постов")],
            [KeyboardButton(text="⚡ Сгенерировать пост сейчас")],
            [KeyboardButton(text="✍️ Написать пост по брифу")],
        ],
        resize_keyboard=True,
    )


def post_actions(post_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=f"accept:{post_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{post_id}"),
            ],
            [
                InlineKeyboardButton(text="🔄 Перегенерировать", callback_data=f"regen:{post_id}"),
                InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit:{post_id}"),
            ],
            [
                InlineKeyboardButton(text="📤 Отправить в канал", callback_data=f"publish:{post_id}"),
            ],
        ]
    )


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🚫 Отмена")]],
        resize_keyboard=True,
    )
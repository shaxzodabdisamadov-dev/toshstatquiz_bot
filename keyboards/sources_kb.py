from typing import Any

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def sources_list_kb(sources: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"📄 {src['title']}", callback_data=f"src:{src['id']}")]
        for src in sources
    ]
    rows.append([InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def source_detail_kb(source_id: str, has_file: bool) -> InlineKeyboardMarkup:
    rows = []
    if has_file:
        rows.append(
            [InlineKeyboardButton(text="⬇️ Faylni yuklab olish", callback_data=f"srcfile:{source_id}")]
        )
    rows.append([InlineKeyboardButton(text="🔙 Manbalar ro'yxati", callback_data="menu:sources")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

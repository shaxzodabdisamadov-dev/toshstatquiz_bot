from __future__ import annotations

import json

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, Message

from config import FILES_DIR, SOURCES_PATH
from keyboards.sources_kb import source_detail_kb, sources_list_kb
from utils.ui import DIVIDER

router = Router(name="sources")


def load_sources() -> list[dict]:
    with open(SOURCES_PATH, encoding="utf-8") as f:
        return json.load(f)["sources"]


def get_source_by_id(source_id: str) -> dict | None:
    for src in load_sources():
        if src["id"] == source_id:
            return src
    return None


SOURCES_INTRO = (
    f"📚 <b>Manbalar</b>\n{DIVIDER}\n\n"
    "Testlar quyidagi rasmiy hujjatlar asosida tuzilgan:"
)


@router.message(Command("manbalar"))
async def cmd_sources(message: Message) -> None:
    sources = load_sources()
    await message.answer(SOURCES_INTRO, reply_markup=sources_list_kb(sources))


@router.callback_query(F.data == "menu:sources")
async def cb_sources_menu(callback: CallbackQuery) -> None:
    sources = load_sources()
    await callback.message.edit_text(SOURCES_INTRO, reply_markup=sources_list_kb(sources))
    await callback.answer()


@router.callback_query(F.data.startswith("src:"))
async def cb_source_detail(callback: CallbackQuery) -> None:
    source_id = callback.data.split(":", 1)[1]
    source = get_source_by_id(source_id)
    if not source:
        await callback.answer("Hujjat topilmadi.", show_alert=True)
        return

    file_name = source.get("file")
    has_file = bool(file_name) and (FILES_DIR / file_name).exists()

    text = f"📄 <b>{source['title']}</b>\n{DIVIDER}\n\n{source.get('description', '')}"
    if file_name and not has_file:
        text += "\n\n⚠️ Fayl hali yuklanmagan."

    await callback.message.edit_text(text, reply_markup=source_detail_kb(source_id, has_file))
    await callback.answer()


@router.callback_query(F.data.startswith("srcfile:"))
async def cb_source_file(callback: CallbackQuery) -> None:
    source_id = callback.data.split(":", 1)[1]
    source = get_source_by_id(source_id)
    if not source or not source.get("file"):
        await callback.answer("Fayl topilmadi.", show_alert=True)
        return

    file_path = FILES_DIR / source["file"]
    if not file_path.exists():
        await callback.answer("Fayl hali yuklanmagan.", show_alert=True)
        return

    await callback.message.answer_document(FSInputFile(file_path))
    await callback.answer()

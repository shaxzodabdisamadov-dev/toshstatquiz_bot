import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.fsm.context import FSMContext

from config import BANNER_PATH, WEBSITE_URL
from database.db import upsert_user
from keyboards.main_menu import back_to_main_kb, main_menu_kb
from utils.ui import DIVIDER

router = Router(name="start")
logger = logging.getLogger(__name__)

GREETING_TEXT = (
    "🇺🇿 <b>TOSHSTAT</b> · Toshkent shahar statistika boshqarmasi\n"
    f"{DIVIDER}\n\n"
    "<b>Mustaqillik — 35 yil</b> 🎉\n\n"
    "O'zbekiston Respublikasi Mustaqilligining <b>35 yilligi</b> bilan chin qalbdan "
    "tabriklaymiz!\n\n"
    "<blockquote>Ushbu bot orqali siz 2026-yilgi biznesni ro'yxatga olish tadbiri "
    "bo'yicha bilimingizni sinab ko'rishingiz va tegishli rasmiy hujjatlar bilan "
    "tanishishingiz mumkin.</blockquote>"
)

MENU_TEXT = "✨ <b>Bosh menyu</b>\nKerakli bo'limni tanlang:"

ABOUT_TEXT = (
    "ℹ️ <b>Bot haqida</b>\n"
    f"{DIVIDER}\n\n"
    "Ushbu bot Toshkent shahar statistika boshqarmasi tomonidan xodimlar va "
    "foydalanuvchilar uchun bilim sinovi (test) va rasmiy ma'lumot manbai sifatida "
    "yaratilgan.\n\n"
    "<b>Buyruqlar</b>\n"
    "/start — botni qayta ishga tushirish\n"
    "/testlar — testlar ro'yxati\n"
    "/manbalar — rasmiy hujjatlar\n"
    "/mynatijalar — mening natijalarim\n"
    "/reyting — eng yaxshi natijalar\n"
    "/yordam — ushbu yordam matni\n\n"
    f"🌐 Rasmiy sayt: {WEBSITE_URL}"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await upsert_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )

    if BANNER_PATH.exists():
        await message.answer_photo(FSInputFile(BANNER_PATH))
    else:
        logger.info("Banner rasmi topilmadi: %s (rasmsiz davom etilmoqda)", BANNER_PATH)

    await message.bot.send_chat_action(message.chat.id, "typing")
    await message.answer(GREETING_TEXT)
    await message.answer(MENU_TEXT, reply_markup=main_menu_kb())


@router.message(Command("yordam"))
async def cmd_help(message: Message) -> None:
    await message.answer(ABOUT_TEXT)


@router.callback_query(F.data == "menu:main")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(MENU_TEXT, reply_markup=main_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "menu:about")
async def cb_about(callback: CallbackQuery) -> None:
    await callback.message.edit_text(ABOUT_TEXT, reply_markup=back_to_main_kb())
    await callback.answer()

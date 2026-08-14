from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import SHOW_LEADERBOARD, WEBSITE_URL


def main_menu_kb() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="🎯 Testlar", callback_data="menu:tests"),
            InlineKeyboardButton(text="📊 Natijalarim", callback_data="menu:myresults"),
        ],
        [
            InlineKeyboardButton(text="📚 Manbalar", callback_data="menu:sources"),
            InlineKeyboardButton(text="🌐 Sayt", url=WEBSITE_URL),
        ],
    ]
    if SHOW_LEADERBOARD:
        rows.append(
            [
                InlineKeyboardButton(text="ℹ️ Yordam", callback_data="menu:about"),
                InlineKeyboardButton(text="🏆 Reyting", callback_data="menu:leaderboard"),
            ]
        )
    else:
        rows.append([InlineKeyboardButton(text="ℹ️ Yordam", callback_data="menu:about")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_to_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:main")],
        ]
    )

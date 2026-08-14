from typing import Any

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.ui import LETTERS


def tests_list_kb(tests: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=f"🔹 {test['title']}  ·  {len(test['questions'])} ta",
                callback_data=f"test:{test['id']}",
            )
        ]
        for test in tests
    ]
    rows.append([InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def quiz_start_kb(test_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Boshlash", callback_data=f"quizstart:{test_id}")],
            [InlineKeyboardButton(text="🔙 Testlar ro'yxati", callback_data="menu:tests")],
        ]
    )


def quiz_options_kb(options: list[str]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"{LETTERS[i]})  {text}", callback_data=f"ans:{i}")]
        for i, text in enumerate(options)
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def next_question_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Keyingi savol  ➜", callback_data="next_q")],
        ]
    )


def result_kb(show_leaderboard: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="🎯 Boshqa test", callback_data="menu:tests"),
            InlineKeyboardButton(text="📊 Natijalarim", callback_data="menu:myresults"),
        ],
    ]
    if show_leaderboard:
        rows.append([InlineKeyboardButton(text="🏆 Reyting", callback_data="menu:leaderboard")])
    rows.append([InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

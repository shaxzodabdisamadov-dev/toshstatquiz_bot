from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import LEADERBOARD_SHOW_NAMES, SHOW_LEADERBOARD
from database.db import get_leaderboard, get_user_results, save_result
from keyboards.main_menu import back_to_main_kb
from keyboards.tests_kb import (
    next_question_kb,
    quiz_options_kb,
    quiz_start_kb,
    result_kb,
    tests_list_kb,
)
from states.quiz import QuizStates
from utils.quiz_logic import (
    build_quiz_session,
    current_question,
    get_test_by_id,
    is_last_question,
    load_tests,
    motivational_message,
)
from utils.ui import DIVIDER, LETTERS, MEDALS, grade, percent_bar

router = Router(name="tests")

TESTS_INTRO = (
    "🎯 <b>Testlar</b>\n"
    f"{DIVIDER}\n\n"
    "2026-yilgi biznesni ro'yxatga olish tadbiri bo'yicha mavzuiy testlar. "
    "Kerakli mavzuni tanlang:"
)


def _question_text(session: dict, index: int, total: int) -> str:
    q = current_question(session)
    return (
        f"🎯 <b>{session['test_title']}</b>\n"
        f"<i>Savol {index + 1}/{total}</i>\n\n"
        f"❓ {q['question']}"
    )


@router.message(Command("testlar"))
async def cmd_tests(message: Message, state: FSMContext) -> None:
    await state.clear()
    tests = load_tests()
    await message.answer(TESTS_INTRO, reply_markup=tests_list_kb(tests))


@router.callback_query(F.data == "menu:tests")
async def cb_tests_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    tests = load_tests()
    await callback.message.edit_text(TESTS_INTRO, reply_markup=tests_list_kb(tests))
    await callback.answer()


@router.callback_query(F.data.startswith("test:"))
async def cb_test_intro(callback: CallbackQuery) -> None:
    test_id = callback.data.split(":", 1)[1]
    test = get_test_by_id(test_id)
    if not test:
        await callback.answer("Test topilmadi.", show_alert=True)
        return

    n = len(test["questions"])
    text = (
        f"🔹 <b>{test['title']}</b>\n"
        f"{DIVIDER}\n\n"
        f"{test.get('description', '')}\n\n"
        f"📋 Savollar soni: <b>{n}</b>\n"
        f"⏱ Taxminiy vaqt: <b>~{n} daqiqa</b>\n\n"
        "Tayyor bo'lsangiz, boshlang!"
    )
    await callback.message.edit_text(text, reply_markup=quiz_start_kb(test_id))
    await callback.answer()


@router.callback_query(F.data.startswith("quizstart:"))
async def cb_quiz_start(callback: CallbackQuery, state: FSMContext) -> None:
    test_id = callback.data.split(":", 1)[1]
    test = get_test_by_id(test_id)
    if not test:
        await callback.answer("Test topilmadi.", show_alert=True)
        return

    session = build_quiz_session(test)
    await state.set_state(QuizStates.in_progress)
    await state.update_data(session=session)

    await callback.bot.send_chat_action(callback.message.chat.id, "typing")

    total = len(session["questions"])
    q = current_question(session)
    await callback.message.edit_text(
        _question_text(session, 0, total),
        reply_markup=quiz_options_kb(q["options"]),
    )
    await callback.answer()


@router.callback_query(QuizStates.in_progress, F.data.startswith("ans:"))
async def cb_quiz_answer(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    session = data["session"]
    total = len(session["questions"])
    q = current_question(session)

    chosen = int(callback.data.split(":", 1)[1])
    correct = q["correct_option"]
    is_correct = chosen == correct

    if is_correct:
        session["correct_count"] += 1
        feedback = "✅ <b>To'g'ri!</b>"
    else:
        correct_text = q["options"][correct]
        feedback = f"❌ <b>Noto'g'ri.</b>\nTo'g'ri javob: <b>{LETTERS[correct]})</b> {correct_text}"

    if q.get("explanation"):
        feedback += f"\n\n<blockquote>💡 {q['explanation']}</blockquote>"

    await state.update_data(session=session)

    index = session["current_index"]
    text = f"{_question_text(session, index, total)}\n\n{feedback}"

    if is_last_question(session):
        await callback.message.edit_text(text)
        await callback.bot.send_chat_action(callback.message.chat.id, "typing")
        await _finish_quiz(callback.message, state, session)
    else:
        await callback.message.edit_text(text, reply_markup=next_question_kb())

    await callback.answer()


@router.callback_query(QuizStates.in_progress, F.data == "next_q")
async def cb_next_question(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    session = data["session"]
    session["current_index"] += 1
    await state.update_data(session=session)

    total = len(session["questions"])
    q = current_question(session)
    await callback.message.edit_text(
        _question_text(session, session["current_index"], total),
        reply_markup=quiz_options_kb(q["options"]),
    )
    await callback.answer()


async def _finish_quiz(message: Message, state: FSMContext, session: dict) -> None:
    total = len(session["questions"])
    correct = session["correct_count"]
    percent = round((correct / total) * 100, 1) if total else 0.0

    await save_result(
        user_id=message.chat.id,
        test_id=session["test_id"],
        test_title=session["test_title"],
        correct_count=correct,
        total_count=total,
    )
    await state.clear()

    badge_emoji, badge_label = grade(percent)
    result_text = (
        "🏁 <b>Test yakunlandi</b>\n"
        f"{DIVIDER}\n\n"
        f"{session['test_title']}\n\n"
        f"{badge_emoji} <b>{badge_label}</b>\n\n"
        f"{percent_bar(percent)}  <b>{percent}%</b>\n\n"
        f"✅ To'g'ri javoblar: <b>{correct}/{total}</b>\n\n"
        f"<i>{motivational_message(percent)}</i>"
    )
    await message.answer(result_text, reply_markup=result_kb(show_leaderboard=SHOW_LEADERBOARD))


@router.message(Command("mynatijalar"))
async def cmd_my_results(message: Message) -> None:
    await _show_my_results(message, message.from_user.id)


@router.callback_query(F.data == "menu:myresults")
async def cb_my_results(callback: CallbackQuery) -> None:
    await _show_my_results(callback.message, callback.from_user.id, edit=True)
    await callback.answer()


async def _show_my_results(message: Message, user_id: int, edit: bool = False) -> None:
    rows = await get_user_results(user_id, limit=10)
    if not rows:
        text = (
            "📊 <b>Mening natijalarim</b>\n"
            f"{DIVIDER}\n\n"
            "Siz hali birorta test topshirmagansiz.\n"
            "🎯 <b>Testlar</b> bo'limidan boshlang."
        )
    else:
        lines = [f"📊 <b>Mening natijalarim</b>\n{DIVIDER}\n"]
        for row in rows:
            badge_emoji, _ = grade(row["percent"])
            lines.append(
                f"{badge_emoji} {row['test_title']}\n"
                f"    {row['correct_count']}/{row['total_count']} · <b>{row['percent']}%</b> · {row['taken_at']}"
            )
        text = "\n".join(lines)

    if edit:
        await message.edit_text(text, reply_markup=back_to_main_kb())
    else:
        await message.answer(text, reply_markup=back_to_main_kb())


@router.message(Command("reyting"))
async def cmd_leaderboard(message: Message) -> None:
    await _show_leaderboard(message)


@router.callback_query(F.data == "menu:leaderboard")
async def cb_leaderboard(callback: CallbackQuery) -> None:
    await _show_leaderboard(callback.message, edit=True)
    await callback.answer()


async def _show_leaderboard(message: Message, edit: bool = False) -> None:
    header = f"🏆 <b>Eng yaxshi natijalar</b>\n{DIVIDER}\n"
    if not SHOW_LEADERBOARD:
        text = f"{header}\nReyting bo'limi hozircha faol emas."
    else:
        rows = await get_leaderboard(limit=10)
        if not rows:
            text = f"{header}\nHozircha natijalar mavjud emas."
        else:
            lines = [header]
            for i, row in enumerate(rows):
                mark = MEDALS[i] if i < len(MEDALS) else f"{i + 1}."
                if LEADERBOARD_SHOW_NAMES:
                    name = row["full_name"] or (f"@{row['username']}" if row["username"] else "Foydalanuvchi")
                else:
                    name = f"Foydalanuvchi #{i + 1}"
                lines.append(f"{mark} {name} — <b>{row['best_percent']}%</b>")
            text = "\n".join(lines)

    if edit:
        await message.edit_text(text, reply_markup=back_to_main_kb())
    else:
        await message.answer(text, reply_markup=back_to_main_kb())

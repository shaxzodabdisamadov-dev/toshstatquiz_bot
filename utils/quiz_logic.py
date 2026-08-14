from __future__ import annotations

import json
import random
from functools import lru_cache
from typing import Any

from config import QUESTIONS_PATH


@lru_cache(maxsize=1)
def load_tests() -> list[dict[str, Any]]:
    with open(QUESTIONS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data["tests"]


def get_test_by_id(test_id: str) -> dict[str, Any] | None:
    for test in load_tests():
        if test["id"] == test_id:
            return test
    return None


def build_quiz_session(test: dict[str, Any]) -> dict[str, Any]:
    """Savollar va variantlar tartibini aralashtirib, yangi test sessiyasi yaratadi."""
    questions = list(test["questions"])
    random.shuffle(questions)

    shuffled_questions = []
    for q in questions:
        options = list(enumerate(q["options"]))  # (original_index, text)
        random.shuffle(options)
        shuffled_questions.append(
            {
                "question": q["question"],
                "explanation": q.get("explanation", ""),
                "options": [text for _, text in options],
                "correct_option": [
                    i for i, (orig_idx, _) in enumerate(options)
                    if orig_idx == q["correct_index"]
                ][0],
            }
        )

    return {
        "test_id": test["id"],
        "test_title": test["title"],
        "questions": shuffled_questions,
        "current_index": 0,
        "correct_count": 0,
    }


def current_question(session: dict[str, Any]) -> dict[str, Any]:
    return session["questions"][session["current_index"]]


def is_last_question(session: dict[str, Any]) -> bool:
    return session["current_index"] >= len(session["questions"]) - 1


def motivational_message(percent: float) -> str:
    if percent >= 90:
        return "Ajoyib! Siz mavzuni mukammal bilasiz."
    if percent >= 70:
        return "Yaxshi natija! Yana bir oz mustahkamlab oling."
    if percent >= 50:
        return "Qoniqarli, lekin hujjatlarni yana ko'rib chiqishingiz tavsiya etiladi."
    return "Ushbu mavzu bo'yicha hujjatlarni qayta o'rganib chiqishingizni tavsiya qilamiz."

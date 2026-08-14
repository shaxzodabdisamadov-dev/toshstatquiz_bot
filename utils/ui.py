from __future__ import annotations

DIVIDER = "⎯" * 22

LETTERS = ["A", "B", "C", "D"]
MEDALS = ["🥇", "🥈", "🥉"]

_FILLED = "●"
_EMPTY = "○"


def bar(fraction: float, width: int = 12) -> str:
    fraction = max(0.0, min(1.0, fraction))
    filled = round(fraction * width)
    return _FILLED * filled + _EMPTY * (width - filled)


def progress_bar(current: int, total: int, width: int = 12) -> str:
    return bar(current / total if total else 0, width)


def percent_bar(percent: float, width: int = 12) -> str:
    return bar(percent / 100, width)


def grade(percent: float) -> tuple[str, str]:
    if percent >= 90:
        return "💎", "A'LO NATIJA"
    if percent >= 70:
        return "🥇", "YAXSHI NATIJA"
    if percent >= 50:
        return "🥈", "QONIQARLI NATIJA"
    return "📕", "MATERIALNI QAYTA O'RGANING"

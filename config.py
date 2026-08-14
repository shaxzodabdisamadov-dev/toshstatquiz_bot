from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "ha")


BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBSITE_URL = os.getenv("WEBSITE_URL", "https://toshstat.uz")
DATABASE_URL = os.getenv("DATABASE_URL", "")
SHOW_LEADERBOARD = _bool(os.getenv("SHOW_LEADERBOARD"), default=True)
LEADERBOARD_SHOW_NAMES = _bool(os.getenv("LEADERBOARD_SHOW_NAMES"), default=False)

DATA_DIR = BASE_DIR / "data"
FILES_DIR = DATA_DIR / "files"
QUESTIONS_PATH = DATA_DIR / "questions.json"
SOURCES_PATH = DATA_DIR / "sources.json"
BANNER_PATH = DATA_DIR / "banner.jpg"

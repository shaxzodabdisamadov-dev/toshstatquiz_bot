from __future__ import annotations

import aiosqlite

from config import DB_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    username    TEXT,
    full_name   TEXT,
    first_seen  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS results (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    test_id       TEXT NOT NULL,
    test_title    TEXT NOT NULL,
    correct_count INTEGER NOT NULL,
    total_count   INTEGER NOT NULL,
    percent       REAL NOT NULL,
    taken_at      TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
"""


async def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_SCHEMA)
        await db.commit()


async def upsert_user(user_id: int, username: str | None, full_name: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, username, full_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name
            """,
            (user_id, username, full_name),
        )
        await db.commit()


async def save_result(
    user_id: int,
    test_id: str,
    test_title: str,
    correct_count: int,
    total_count: int,
) -> None:
    percent = round((correct_count / total_count) * 100, 1) if total_count else 0.0
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO results (user_id, test_id, test_title, correct_count, total_count, percent)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, test_id, test_title, correct_count, total_count, percent),
        )
        await db.commit()


async def get_user_results(user_id: int, limit: int = 10) -> list[aiosqlite.Row]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT test_title, correct_count, total_count, percent, taken_at
            FROM results
            WHERE user_id = ?
            ORDER BY taken_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        return await cursor.fetchall()


async def get_leaderboard(limit: int = 10) -> list[aiosqlite.Row]:
    """Har bir foydalanuvchining eng yaxshi natijasi bo'yicha reyting."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT u.user_id, u.username, u.full_name,
                   MAX(r.percent) AS best_percent,
                   r.test_title
            FROM results r
            JOIN users u ON u.user_id = r.user_id
            GROUP BY r.user_id
            ORDER BY best_percent DESC
            LIMIT ?
            """,
            (limit,),
        )
        return await cursor.fetchall()

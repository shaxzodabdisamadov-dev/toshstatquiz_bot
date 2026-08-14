from __future__ import annotations

import asyncpg

from config import DATABASE_URL

_pool: asyncpg.Pool | None = None

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id     BIGINT PRIMARY KEY,
    username    TEXT,
    full_name   TEXT,
    first_seen  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS results (
    id            SERIAL PRIMARY KEY,
    user_id       BIGINT NOT NULL REFERENCES users (user_id),
    test_id       TEXT NOT NULL,
    test_title    TEXT NOT NULL,
    correct_count INTEGER NOT NULL,
    total_count   INTEGER NOT NULL,
    percent       DOUBLE PRECISION NOT NULL,
    taken_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


async def init_db() -> None:
    global _pool
    _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    async with _pool.acquire() as conn:
        await conn.execute(_SCHEMA)


def _get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Baza ulanish puli ishga tushirilmagan — avval init_db() chaqiring.")
    return _pool


async def upsert_user(user_id: int, username: str | None, full_name: str) -> None:
    async with _get_pool().acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (user_id, username, full_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE SET
                username = EXCLUDED.username,
                full_name = EXCLUDED.full_name
            """,
            user_id, username, full_name,
        )


async def save_result(
    user_id: int,
    test_id: str,
    test_title: str,
    correct_count: int,
    total_count: int,
) -> None:
    percent = round((correct_count / total_count) * 100, 1) if total_count else 0.0
    async with _get_pool().acquire() as conn:
        await conn.execute(
            """
            INSERT INTO results (user_id, test_id, test_title, correct_count, total_count, percent)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            user_id, test_id, test_title, correct_count, total_count, percent,
        )


async def get_user_results(user_id: int, limit: int = 10) -> list[asyncpg.Record]:
    async with _get_pool().acquire() as conn:
        return await conn.fetch(
            """
            SELECT test_title, correct_count, total_count, percent, taken_at
            FROM results
            WHERE user_id = $1
            ORDER BY taken_at DESC
            LIMIT $2
            """,
            user_id, limit,
        )


async def get_leaderboard(limit: int = 10) -> list[asyncpg.Record]:
    """Har bir foydalanuvchining eng yaxshi natijasi bo'yicha reyting."""
    async with _get_pool().acquire() as conn:
        return await conn.fetch(
            """
            SELECT u.user_id, u.username, u.full_name,
                   best.percent AS best_percent, best.test_title
            FROM (
                SELECT DISTINCT ON (user_id) user_id, percent, test_title
                FROM results
                ORDER BY user_id, percent DESC
            ) best
            JOIN users u ON u.user_id = best.user_id
            ORDER BY best.percent DESC
            LIMIT $1
            """,
            limit,
        )

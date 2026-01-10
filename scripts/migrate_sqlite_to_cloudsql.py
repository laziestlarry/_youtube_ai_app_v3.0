#!/usr/bin/env python3
"""
Migrate SQLite data to Cloud SQL (Postgres).

Usage:
  DATABASE_URL=postgresql+asyncpg://... python scripts/migrate_sqlite_to_cloudsql.py

Optional env:
  SQLITE_PATH=./youtube_ai.db
  BATCH_SIZE=500
  TRUNCATE_FIRST=false
"""

import asyncio
import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine

from backend.core.database import Base

# Import models to register metadata for create_all.
from backend.models import user  # noqa: F401
from backend.models import youtube  # noqa: F401
from backend.models import content  # noqa: F401
from backend.models import workflow  # noqa: F401
from backend.models import subscription  # noqa: F401
from backend.models import bizop  # noqa: F401
from backend.models import channel  # noqa: F401
from backend.models import video  # noqa: F401

JSON_COLUMNS: Dict[str, Sequence[str]] = {
    "biz_opportunities": ("tags", "metadata", "raw_data"),
    "content_ideas": ("generated_content",),
}

BOOLEAN_COLUMNS: Dict[str, Sequence[str]] = {
    "users": ("is_active", "is_superuser"),
    "channels": ("is_active",),
}

DATETIME_COLUMNS = {
    "created_at",
    "updated_at",
    "timestamp",
    "fetched_at",
    "upload_date",
    "published_at",
    "youtube_token_expiry",
    "current_period_start",
    "current_period_end",
    "date",
}

PREFERRED_TABLE_ORDER = [
    "users",
    "channels",
    "channel_stats",
    "video_analytics",
    "videos",
    "content_ideas",
    "workflow_columns",
    "workflow_cards",
    "biz_opportunities",
    "user_subscriptions",
    "video_revenue",
    "digital_products",
    "affiliate_links",
    "affiliate_clicks",
    "affiliate_conversions",
    "payment_transactions",
]


def normalize_asyncpg_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)
    if url.startswith("postgres+asyncpg://"):
        return url.replace("postgres+asyncpg://", "postgresql://", 1)
    return url


def parse_value(table: str, column: str, value):
    if value is None:
        return None
    if column in DATETIME_COLUMNS and isinstance(value, str):
        raw = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(raw)
        except ValueError:
            return value
    if table in JSON_COLUMNS and column in JSON_COLUMNS[table]:
        if isinstance(value, (dict, list)):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
    if table in BOOLEAN_COLUMNS and column in BOOLEAN_COLUMNS[table]:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            lowered = value.lower()
            if lowered in ("true", "1", "t", "yes", "y"):
                return True
            if lowered in ("false", "0", "f", "no", "n"):
                return False
    return value


def fetch_table_names(conn: sqlite3.Connection) -> List[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    tables = [row[0] for row in rows if row[0] != "sqlite_sequence"]
    ordered = [t for t in PREFERRED_TABLE_ORDER if t in tables]
    ordered.extend([t for t in tables if t not in ordered])
    return ordered


def fetch_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [row[1] for row in rows]


async def ensure_schema(database_url: str) -> None:
    engine = create_async_engine(database_url, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def migrate_table(
    pg_conn: asyncpg.Connection,
    sqlite_conn: sqlite3.Connection,
    table: str,
    batch_size: int,
    truncate_first: bool,
) -> None:
    columns = fetch_columns(sqlite_conn, table)
    if not columns:
        print(f"Skipping {table}: no columns detected")
        return

    quoted_columns = [f"\"{col}\"" for col in columns]
    placeholders = ", ".join(f"${idx}" for idx in range(1, len(columns) + 1))
    insert_sql = (
        f'INSERT INTO "{table}" ({", ".join(quoted_columns)}) '
        f"VALUES ({placeholders}) ON CONFLICT DO NOTHING"
    )

    if truncate_first:
        await pg_conn.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')

    cursor = sqlite_conn.execute(f'SELECT {", ".join(quoted_columns)} FROM "{table}"')
    rows = cursor.fetchall()
    if not rows:
        print(f"✓ {table}: 0 rows")
        return

    batch: List[Tuple] = []
    total = 0
    for row in rows:
        parsed = tuple(
            parse_value(table, column, value)
            for column, value in zip(columns, row)
        )
        batch.append(parsed)
        if len(batch) >= batch_size:
            await pg_conn.executemany(insert_sql, batch)
            total += len(batch)
            batch.clear()

    if batch:
        await pg_conn.executemany(insert_sql, batch)
        total += len(batch)

    sequence_name = await pg_conn.fetchval(
        "SELECT pg_get_serial_sequence($1, 'id')",
        table,
    )
    if sequence_name:
        await pg_conn.execute(
            f'SELECT setval($1, COALESCE(MAX(id), 1), true) FROM "{table}"',
            sequence_name,
        )

    print(f"✓ {table}: {total} rows")


async def run_migration() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL must be set for Postgres target.")

    sqlite_path = os.getenv("SQLITE_PATH", "./youtube_ai.db")
    batch_size = int(os.getenv("BATCH_SIZE", "500"))
    truncate_first = os.getenv("TRUNCATE_FIRST", "false").lower() in ("1", "true", "yes")

    if not os.path.exists(sqlite_path):
        raise SystemExit(f"SQLite file not found: {sqlite_path}")

    await ensure_schema(database_url)

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row

    pg_url = normalize_asyncpg_url(database_url)
    pg_conn = await asyncpg.connect(pg_url)
    try:
        tables = fetch_table_names(sqlite_conn)
        print(f"Tables: {', '.join(tables)}")
        for table in tables:
            async with pg_conn.transaction():
                await migrate_table(
                    pg_conn,
                    sqlite_conn,
                    table,
                    batch_size=batch_size,
                    truncate_first=truncate_first,
                )
    finally:
        await pg_conn.close()
        sqlite_conn.close()


def main() -> None:
    asyncio.run(run_migration())


if __name__ == "__main__":
    main()

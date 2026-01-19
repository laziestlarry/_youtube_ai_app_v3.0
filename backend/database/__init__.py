 
"""Database helpers for analytics modules."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from backend.core.database import (  # noqa: F401
    Base,
    AsyncSessionLocal,
    SessionLocal,
    create_database_engines,
    engine,
    get_async_db,
    get_db,
    init_db,
)


def _resolve_sqlite_path() -> str:
    data_dir = Path(os.getenv("DATA_DIR", ".")).resolve()
    url = os.getenv("DATABASE_URL", f"sqlite:///{data_dir / 'youtube_ai.db'}")
    if url.startswith("sqlite:////"):
        return url.replace("sqlite:////", "/")
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "")
    return str(data_dir / "youtube_ai.db")


def get_db_connection() -> sqlite3.Connection:
    """Return a sqlite connection for lightweight analytics helpers."""
    path = _resolve_sqlite_path()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)


def get_all_ideas(limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch video ideas if the table exists; otherwise return empty list."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM video_ideas LIMIT ?", (limit,))
        except sqlite3.Error:
            return []
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description or []]
        return [dict(zip(columns, row)) for row in rows]


def insert_idea(
    title: str,
    category: str,
    expected_views: int = 0,
    metadata: Dict[str, Any] | None = None,
    tags: List[str] | None = None,
    script: str | None = None,
    thumbnail_path: str | None = None,
    audio_path: str | None = None,
) -> str:
    """Insert a content idea into the primary database."""
    from uuid import uuid4
    from datetime import datetime
    from backend.models.content import ContentIdea

    if SessionLocal is None:
        create_database_engines()

    idea_id = str(uuid4())
    payload = metadata.copy() if metadata else {}
    payload.update(
        {
            "expected_views": expected_views,
            "tags": tags or [],
            "script": script,
            "thumbnail_path": thumbnail_path,
            "audio_path": audio_path,
            "created_at": datetime.utcnow().isoformat(),
        }
    )

    db = SessionLocal()
    try:
        db.add(
            ContentIdea(
                id=idea_id,
                title=title,
                description=script or "",
                category=category,
                priority=3,
                status="generated",
                generated_content=payload,
            )
        )
        db.commit()
    finally:
        db.close()
    return idea_id


def fetch_all_ideas(limit: int = 100) -> List[tuple]:
    """Return content ideas in a legacy tuple format."""
    from backend.models.content import ContentIdea

    if SessionLocal is None:
        create_database_engines()

    db = SessionLocal()
    try:
        rows = (
            db.query(ContentIdea)
            .order_by(ContentIdea.created_at.desc())
            .limit(limit)
            .all()
        )
        output: List[tuple] = []
        for row in rows:
            expected_views = 0
            if isinstance(row.generated_content, dict):
                expected_views = int(row.generated_content.get("expected_views") or 0)
            output.append(
                (
                    row.id,
                    row.title,
                    row.category,
                    expected_views,
                    row.created_at,
                    row.status,
                )
            )
        return output
    finally:
        db.close()

import aiosqlite
import logging
import os # Import os module
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration: Use an environment variable for flexibility
# Default to a file in the current working directory if not set
DATABASE_URL = os.getenv("DATABASE_URL", "./youtube_app_enhanced.db")

@asynccontextmanager
async def get_db():
    """Provides an asynchronous database connection."""
    conn = None
    try:
        # Ensure the directory for the database file exists
        db_dir = os.path.dirname(DATABASE_URL)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Created database directory: {db_dir}")

        conn = await aiosqlite.connect(DATABASE_URL)
        conn.row_factory = aiosqlite.Row
        yield conn
    except aiosqlite.Error as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            await conn.close()

async def init_db():
    """Initializes the database and creates tables if they don't exist."""
    async with get_db() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS video_ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                topic TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea_id INTEGER,
                title TEXT,
                script TEXT,
                video_path TEXT,
                thumbnail_path TEXT,
                status TEXT DEFAULT 'processing',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (idea_id) REFERENCES video_ideas (id)
            )
        ''')
        await conn.commit()
    logger.info("Database initialized successfully.")

async def add_user(user_id: str, username: str) -> None:
    async with get_db() as conn:
        await conn.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (user_id, username))
        await conn.commit()

async def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    async with get_db() as conn:
        async with conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def add_video_idea(user_id: str, topic: str) -> int:
    async with get_db() as conn:
        async with conn.execute("INSERT INTO video_ideas (user_id, topic) VALUES (?, ?)", (user_id, topic)) as cursor:
            await conn.commit()
            return cursor.lastrowid

async def get_video_idea(idea_id: int) -> Optional[Dict[str, Any]]:
    async with get_db() as conn:
        async with conn.execute("SELECT * FROM video_ideas WHERE id = ?", (idea_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def update_video_idea_status(idea_id: int, status: str) -> None:
    async with get_db() as conn:
        await conn.execute("UPDATE video_ideas SET status = ? WHERE id = ?", (status, idea_id))
        await conn.commit()

async def add_video_record(idea_id: int, title: str, script: str, video_path: str, thumbnail_path: str) -> int:
    async with get_db() as conn:
        async with conn.execute(
            "INSERT INTO videos (idea_id, title, script, video_path, thumbnail_path, status) VALUES (?, ?, ?, ?, ?, 'completed')",
            (idea_id, title, script, video_path, thumbnail_path)
        ) as cursor:
            await conn.commit()
            return cursor.lastrowid

async def get_user_videos(user_id: str) -> List[Dict[str, Any]]:
    async with get_db() as conn:
        query = """
            SELECT v.*, vi.topic FROM videos v
            JOIN video_ideas vi ON v.idea_id = vi.id
            WHERE vi.user_id = ?
            ORDER BY v.created_at DESC
        """
        async with conn.execute(query, (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

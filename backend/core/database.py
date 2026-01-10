"""
Database configuration and initialization.
"""

import asyncio
import logging
from pathlib import Path
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import func

from backend.core.config import settings

logger = logging.getLogger(__name__)

# Create declarative base
Base = declarative_base()


# Database engines
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None

def get_database_url(async_mode: bool = False) -> str:
    """Get database URL for sync or async mode."""
    url = settings.database_url
    
    # Ensure we have a valid URL
    if not url or url.strip() == "":
        url = "sqlite:///./youtube_ai.db"

    # RESILIENCE: Check if Cloud SQL socket exists if specified
    if "host=/cloudsql/" in url:
        import re
        match = re.search(r"host=([^&?]+)", url)
        if match:
            socket_path = match.group(1)
            # If we're not on Linux or the path definitely doesn't exist, fallback
            if not Path(socket_path).exists():
                logger.warning(f"Cloud SQL socket path {socket_path} not found. Falling back to local SQLite.")
                url = "sqlite:///./youtube_ai.db"
    
    if url.startswith("sqlite:///"):
        if async_mode:
            return url.replace("sqlite:///", "sqlite+aiosqlite:///")
        return url
    
    if "postgresql" in url:
        if async_mode:
            if "asyncpg" not in url:
                return url.replace("postgresql://", "postgresql+asyncpg://")
            return url
        else:
            if "asyncpg" in url:
                return url.replace("postgresql+asyncpg://", "postgresql://")
            return url
    
    return url

def create_database_engines():
    """Create database engines."""
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    
    # Sync engine
    sync_url = get_database_url(async_mode=False)
    engine = create_engine(
        sync_url,
        echo=settings.debug,
        poolclass=StaticPool if "sqlite" in sync_url else None,
        connect_args={"check_same_thread": False} if "sqlite" in sync_url else {}
    )
    
    # Async engine
    async_url = get_database_url(async_mode=True)
    async_engine = create_async_engine(
        async_url,
        echo=settings.debug,
        poolclass=StaticPool if "sqlite" in async_url else None,
        connect_args={"check_same_thread": False} if "sqlite" in async_url else {}
    )
    
    # Session makers
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    AsyncSessionLocal = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

def get_db():
    """Get database session (sync)."""
    if engine is None:
        create_database_engines()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    """Get database session (async)."""
    if async_engine is None:
        create_database_engines()
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """Initialize database tables."""
    try:
        # Ensure database directory exists
        db_url = get_database_url()
        if db_url.startswith("sqlite:///"):
            db_path = db_url.replace("sqlite:///", "")
            if db_path.startswith("./"):
                db_dir = Path(db_path).parent
                db_dir.mkdir(parents=True, exist_ok=True)
        
        # Create engines if not already created
        if engine is None:
            create_database_engines()
        
        # Create tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
        return {"status": "success", "message": "Database initialized"}
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

async def check_db_health():
    """Check database health."""
    try:
        if async_engine is None:
            create_database_engines()
            
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        return {"status": "healthy", "message": "Database connection successful"}
        
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {"status": "unhealthy", "message": str(e)}

# Engines are now initialized lazily in get_db, get_async_db, init_db, and check_db_health
# create_database_engines()
#!/usr/bin/env python3
"""
Simple database initialization script.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def ensure_directories():
    """Ensure required directories exist."""
    directories = [
        "logs",
        "uploads", 
        "backups",
        "static",
        "static/output",
        "static/audio",
        "static/thumbnails"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory ensured: {directory}")

async def main():
    """Initialize the database."""
    try:
        print("🎯 Initializing YouTube AI Content Creator Database")
        print("=" * 50)
        
        # Ensure directories exist
        print("📁 Creating directories...")
        ensure_directories()
        
        # Import and check configuration
        print("⚙️  Loading configuration...")
        from backend.core.config import settings
        print(f"📊 Database URL: {settings.database_url}")
        
        # Validate database URL
        if not settings.database_url or settings.database_url.strip() == "":
            print("❌ Database URL is empty, using default")
            settings.database_url = "sqlite:///./youtube_ai.db"
        
        # Initialize database
        print("🗄️  Initializing database...")
        from backend.core.database import init_db
        result = await init_db()
        print(f"✅ {result['message']}")
        
        # Check if database file was created (for SQLite)
        if settings.database_url.startswith("sqlite:///"):
            db_path = settings.database_url.replace("sqlite:///", "")
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                print(f"📊 Database file created: {db_path} ({size} bytes)")
            else:
                print(f"⚠️  Database file not found: {db_path}")
        
        print("\n🎉 Database initialization complete!")
        return 0
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
import sys
import asyncio
from pathlib import Path

# Ensure repo root is in the path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.core import database as db

if __name__ == "__main__":
    try:
        asyncio.run(db.init_db())
        print("✅ Database initialized successfully (custom SQLite logic)")
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        sys.exit(1) 

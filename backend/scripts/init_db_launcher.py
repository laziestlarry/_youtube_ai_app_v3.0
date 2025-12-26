import sys
import os
from pathlib import Path

# Ensure backend is in the path
sys.path.append(str(Path(__file__).parent.parent))

from database import init_db

if __name__ == "__main__":
    try:
        init_db()
        print("✅ Database initialized successfully (custom SQLite logic)")
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        sys.exit(1) 
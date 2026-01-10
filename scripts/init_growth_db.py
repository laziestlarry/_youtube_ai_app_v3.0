from sqlalchemy import create_engine
from modules.growth_engine_v1.models import Base
from modules.growth_engine_v1.config import settings
import os

def init_db():
    db_url = settings.GROWTH_DATABASE_URL
    # Ensure sync driver
    if "aiosqlite" in db_url:
        db_url = db_url.replace("sqlite+aiosqlite:///", "sqlite:/// ")
    
    print(f"🛠️ Initializing Growth Engine Database: {db_url}")
    
    engine = create_engine(db_url.strip(), connect_args={"check_same_thread": False})
    
    # This will create all tables registered with this Base
    Base.metadata.create_all(bind=engine)
    
    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"✅ Tables created: {tables}")

if __name__ == "__main__":
    init_db()

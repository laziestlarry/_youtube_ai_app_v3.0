import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from database import Base, engine
from models import (
    User,
    VideoIdea,
    Video,
    Script,
    Thumbnail,
    Audio,
    Analytics,
    Monetization,
    ContentStrategy
)

def init_database():
    """Initialize the database with all required tables."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Create initial admin user if not exists
        from database import SessionLocal
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        db = SessionLocal()
        
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            admin = User(
                email="admin@example.com",
                hashed_password=pwd_context.hash("admin123"),  # Change this in production
                is_active=True,
                is_admin=True
            )
            db.add(admin)
            db.commit()
            print("✅ Admin user created successfully")
        
        db.close()
        print("✅ Database initialization completed")
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_database() 
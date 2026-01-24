import os
import sys
from pathlib import Path

# Add repo root to the Python path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.core import database as db
from backend.core.database import Base
from backend.models.user import User
from backend.models import bizop, channel, content, revenue, subscription, video, workflow, youtube, commerce  # noqa: F401

def init_database():
    """Initialize the database with all required tables."""
    try:
        # Create all tables
        if db.engine is None:
            db.create_database_engines()
        Base.metadata.create_all(bind=db.engine)
        print("✅ Database tables created successfully")
        
        # Create initial admin user if not exists
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        db_session = db.SessionLocal()

        admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
        admin_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD")
        environment = os.getenv("ENVIRONMENT", "").lower()
        if not admin_password and environment in ("production", "prod"):
            print("⚠️  DEFAULT_ADMIN_PASSWORD not set. Skipping admin seed in production.")
            db_session.close()
            return
        if not admin_password:
            admin_password = "admin123"
            print("⚠️  DEFAULT_ADMIN_PASSWORD not set. Using dev default for admin seed.")

        admin = db_session.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                username=admin_username,
                hashed_password=pwd_context.hash(admin_password),
                is_active=True,
                is_superuser=True
            )
            db_session.add(admin)
            db_session.commit()
            print("✅ Admin user created successfully")
        
        db_session.close()
        print("✅ Database initialization completed")
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_database() 

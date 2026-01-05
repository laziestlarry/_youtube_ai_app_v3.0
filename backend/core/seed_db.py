import logging
from sqlalchemy import select
import backend.core.database as database
from backend.models.user import User
from backend.core.security import get_password_hash
from backend.core.config import settings

logger = logging.getLogger(__name__)

async def seed_db():
    """Seed the database with initial data (e.g., default admin user)."""
    async with database.AsyncSessionLocal() as db:
        try:
            # Check if admin user exists
            admin_email = "admin@example.com"
            result = await db.execute(select(User).where(User.email == admin_email))
            admin_user = result.scalars().first()
            
            if not admin_user:
                logger.info(f"Admin user {admin_email} not found. Creating...")
                admin_username = "admin"
                admin_password = "admin123" 
                
                db_user = User(
                    email=admin_email,
                    username=admin_username,
                    hashed_password=get_password_hash(admin_password),
                    is_active=True,
                    is_superuser=True
                )
                db.add(db_user)
                await db.commit()
                logger.info(f"Default admin user created: {admin_email} / {admin_password}")
            else:
                logger.info(f"Admin user {admin_email} already exists. Skipping seed.")
        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            await db.rollback()
